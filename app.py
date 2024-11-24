import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/AngelUrielLopezVazquez/INTROCD/refs/heads/main/Base_Limpia.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Analisis de Tendencias Globales de Ataques Terroristas Utilizando la Base de datos 'Global Terrorism Database' (GTD)", className="text-center my-4 text-dark"),

    dbc.Row([
        dbc.Col([
            html.Label("Selecciona una Región:", className="fw-bold text-dark"),
            dcc.Dropdown(
                id='region-filter',
                options=[{'label': region, 'value': region} for region in df['Region'].unique()],
                value=None,
                placeholder="Selecciona una Región",
                className="mb-3"
            )
        ], width=4),
        dbc.Col([
            html.Label("Selecciona un Tipo de Ataque:", className="fw-bold text-dark"),
            dcc.Dropdown(
                id='attack-type-filter',
                options=[{'label': attack, 'value': attack} for attack in df['Tipo_Ataque'].unique()],
                value=None,
                placeholder="Selecciona un Tipo de Ataque",
                className="mb-3"
            )
        ], width=4),
        dbc.Col([
            html.Label("Selecciona un Perpetrador:", className="fw-bold text-dark"),
            dcc.Dropdown(
                id='perpetrator-filter',
                options=[{'label': perpetrator, 'value': perpetrator} for perpetrator in df['Perpetrador'].unique()],
                value=None,
                placeholder="Selecciona un Perpetrador",
                className="mb-3"
            )
        ], width=4),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Selecciona un Año:", className="fw-bold text-dark"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in range(df['Año'].min(), df['Año'].max() + 1)],
                value=None,
                placeholder="Selecciona un Año",
                className="mb-3"
            )
        ], width=4),
        dbc.Col([
            html.Label("Rango de Muertos:", className="fw-bold text-dark"),
            dcc.RangeSlider(
                id='deaths-range-slider',
                min=0,
                max=df['Muertos'].max(),
                step=1,
                marks={i: str(i) for i in range(0, df['Muertos'].max(), 1000)},
                value=[0, df['Muertos'].max()]
            )
        ], width=4),
        dbc.Col([
            html.Label("Rango de Heridos:", className="fw-bold text-dark"),
            dcc.RangeSlider(
                id='injuries-range-slider',
                min=0,
                max=df['Heridos'].max(),
                step=1,
                marks={i: str(i) for i in range(0, df['Heridos'].max(), 1000)},
                value=[0, df['Heridos'].max()]
            )
        ], width=4),
    ]),

    dbc.Row([
        dbc.Col(html.Div(f"Total de Ataques Registrados: {df.shape[0]}", className="text-center text-dark"), width=4),
        dbc.Col(html.Div(f"Muertos Totales Registradas: {df['Muertos'].sum()}", className="text-center text-dark"), width=4),
        dbc.Col(html.Div(f"Heridos Totales Registrados: {df['Heridos'].sum()}", className="text-center text-dark"), width=4),
    ], className="my-3"),

    dbc.Row([
        dbc.Col(html.Div("📈 Aumento de ataques en los últimos años", className="text-center text-danger", style={'fontSize': 18}))
    ]),

    dbc.Row([
        dbc.Col(dbc.Button('Resetear Filtros', id='reset-button', color='primary', n_clicks=0), width=12)
    ], className="my-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='attacks-by-country-chart'), width=6),
        dbc.Col(dcc.Graph(id='casualties-by-attack-type-chart'), width=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='timeline-chart'), width=12),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='damage-by-region-chart'), width=6),
        dbc.Col(dcc.Graph(id='death-injury-comparison'), width=6)
    ], className="mt-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='geo-map-chart'), width=12)
    ], className="mt-4"),
])

@app.callback(
    [Output('attacks-by-country-chart', 'figure'),
     Output('casualties-by-attack-type-chart', 'figure'),
     Output('timeline-chart', 'figure'),
     Output('damage-by-region-chart', 'figure'),
     Output('death-injury-comparison', 'figure'),
     Output('geo-map-chart', 'figure')],
    [Input('region-filter', 'value'),
     Input('attack-type-filter', 'value'),
     Input('perpetrator-filter', 'value'),
     Input('year-dropdown', 'value'),
     Input('deaths-range-slider', 'value'),
     Input('injuries-range-slider', 'value'),
     Input('reset-button', 'n_clicks')]
)
def update_charts(selected_region, selected_attack_type, selected_perpetrator, selected_year, selected_deaths_range, selected_injuries_range, reset_click):

    if reset_click > 0:
        selected_region = None
        selected_attack_type = None
        selected_perpetrator = None
        selected_year = None
        selected_deaths_range = [0, df['Muertos'].max()]
        selected_injuries_range = [0, df['Heridos'].max()]

    dff = df.copy()

    if selected_region:
        dff = dff[dff['Region'] == selected_region]
    if selected_attack_type:
        dff = dff[dff['Tipo_Ataque'] == selected_attack_type]
    if selected_perpetrator:
        dff = dff[dff['Perpetrador'] == selected_perpetrator]
    if selected_year:
        dff = dff[dff['Año'] == selected_year]

    dff = dff[(dff['Muertos'] >= selected_deaths_range[0]) & (dff['Muertos'] <= selected_deaths_range[1])]
    dff = dff[(dff['Heridos'] >= selected_injuries_range[0]) & (dff['Heridos'] <= selected_injuries_range[1])]

    trend_dff = df.copy()
    if selected_region:
        trend_dff = trend_dff[trend_dff['Region'] == selected_region]
    if selected_attack_type:
        trend_dff = trend_dff[trend_dff['Tipo_Ataque'] == selected_attack_type]
    if selected_perpetrator:
        trend_dff = trend_dff[trend_dff['Perpetrador'] == selected_perpetrator]
    trend_dff = trend_dff[(trend_dff['Muertos'] >= selected_deaths_range[0]) & (trend_dff['Muertos'] <= selected_deaths_range[1])]
    trend_dff = trend_dff[(trend_dff['Heridos'] >= selected_injuries_range[0]) & (trend_dff['Heridos'] <= selected_injuries_range[1])]

    attacks_by_country_chart = px.bar(
        dff.groupby('Pais').size().reset_index(name='Número de Ataques'),
        x='Pais', y='Número de Ataques', color='Pais',
        title="Número de Ataques por País"
    )

    casualties_by_attack_type_chart = px.bar(
        dff.groupby('Tipo_Ataque')[['Muertos', 'Heridos']].sum().reset_index(),
        x='Tipo_Ataque', y=['Muertos', 'Heridos'], barmode='group',
        title="Número de Muertos y Heridos por Tipo de Ataque"
    )

    timeline_chart = px.line(
        trend_dff.groupby('Año').size().reset_index(name='Número de Ataques'),
        x='Año', y='Número de Ataques',
        title="Tendencia de Ataques a lo Largo de los Años"
    )

    damage_by_region_chart = px.bar(
        dff.groupby('Region')[['Daño_Propiedad']].sum().reset_index(),
        x='Region', y='Daño_Propiedad', color='Region',
        title="Daño por Región"
    )

    death_injury_comparison = px.scatter(
        dff, x='Muertos', y='Heridos', color='Tipo_Ataque',
        title="Comparación de Muertos vs Heridos por Tipo de Ataque"
    )

    geo_map_chart = px.scatter_geo(
        dff, lat='Latitud', lon='Longitud', hover_name='Pais', size='Muertos',
        title="Distribución Geográfica de los Ataques"
    )

    return (attacks_by_country_chart, casualties_by_attack_type_chart, timeline_chart, 
            damage_by_region_chart, death_injury_comparison, geo_map_chart)

if __name__ == '__main__':
    app.run_server(debug=True)