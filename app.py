# Importación de las herramientas requeridas
import pandas as pd
import json
from dash import Dash, html, dcc
import plotly.graph_objs as go

# 1. CARGA DE ARCHIVOS
df_mortalidad = pd.read_excel('data/AnexoFetal2019.xlsx', dtype={'COD_DEPARTAMENTO': str, 'COD_MUNICIPIO': str})
df_divipola = pd.read_excel('data/Divipola.xlsx', dtype={'COD_DEPARTAMENTO': str, 'COD_MUNICIPIO': str})
df_codigos = pd.read_excel('data/AnexoCodigosDeMuerte.xlsx', dtype={'CodigoDeLaCIE10TresCaracteres': str})

with open('data/Colombia.geo.json', encoding='utf-8') as f:
    geojson_colombia = json.load(f)

# 2. ESTANDARIZACIÓN GEOGRÁFICA
df_mortalidad['COD_DEPARTAMENTO'] = df_mortalidad['COD_DEPARTAMENTO'].str.zfill(2)
df_mortalidad['COD_MUNICIPIO'] = df_mortalidad['COD_MUNICIPIO'].str.zfill(3)

df_divipola['COD_DEPARTAMENTO'] = df_divipola['COD_DEPARTAMENTO'].str.zfill(2)
df_divipola['COD_MUNICIPIO'] = df_divipola['COD_MUNICIPIO'].str.zfill(3)

# Se eliminan filas duplicadas en el diccionario Divipola
df_divipola = df_divipola.drop_duplicates(subset=['COD_DEPARTAMENTO', 'COD_MUNICIPIO'])

# 3. UNIÓN DE BASES DE DATOS (MERGE)
df_completo = pd.merge(
    df_mortalidad,
    df_divipola,
    on=['COD_DEPARTAMENTO', 'COD_MUNICIPIO'],
    how='left'
)

# Extracción de los 3 primeros caracteres del código de muerte
df_completo['CODIGO_3'] = df_completo['COD_MUERTE'].astype(str).str[:3]

df_codigos = df_codigos.drop_duplicates(subset=['CodigoDeLaCIE10TresCaracteres'])
df_completo = pd.merge(
    df_completo,
    df_codigos,
    left_on='CODIGO_3',
    right_on='CodigoDeLaCIE10TresCaracteres',
    how='left'
)

df_completo.rename(columns={'DescripcionDeCodigosMortalidadATresCaracteres': 'CAUSA_MUERTE'}, inplace=True)

# 4. TRADUCCIÓN DE VARIABLES
df_completo['SEXO'] = df_completo['SEXO'].map({1: 'Masculino', 2: 'Femenino', 3: 'Indeterminado'})

def mapear_edad(codigo):
    try:
        codigo = int(codigo)
        if 0 <= codigo <= 4: return 'Mortalidad neonatal'
        elif 5 <= codigo <= 6: return 'Mortalidad infantil'
        elif 7 <= codigo <= 8: return 'Primera infancia'
        elif 9 <= codigo <= 10: return 'Niñez'
        elif codigo == 11: return 'Adolescencia'
        elif 12 <= codigo <= 13: return 'Juventud'
        elif 14 <= codigo <= 16: return 'Adultez temprana'
        elif 17 <= codigo <= 19: return 'Adultez intermedia'
        elif 20 <= codigo <= 24: return 'Vejez'
        elif 25 <= codigo <= 28: return 'Longevidad / Centenarios'
        elif codigo == 29: return 'Edad desconocida'
        else: return 'Sin clasificación'
    except:
        return 'Sin clasificación'

df_completo['CATEGORIA_EDAD'] = df_completo['GRUPO_EDAD1'].apply(mapear_edad)

# 5. PALETA DE COLORES OFICIAL
colores = {
    'oscuro': '#033259',
    'medio': '#1D3E5E',
    'claro': '#CFE2FF',
    'blanco': '#FFFFFF',
    'texto': '#222222'
}

# 6. CONSTRUCCIÓN DE GRÁFICOS INTERACTIVOS

# 6.1 Mapa coroplético
mapa_data = df_completo.groupby('COD_DEPARTAMENTO').size().reset_index(name='TOTAL_MUERTES')
fig_mapa = go.Figure(go.Choroplethmapbox(
    geojson=geojson_colombia,
    locations=mapa_data['COD_DEPARTAMENTO'],
    featureidkey="properties.DPTO",
    z=mapa_data['TOTAL_MUERTES'],
    colorscale=[[0, colores['claro']], [1, colores['oscuro']]],
    text=mapa_data['COD_DEPARTAMENTO'],
    hovertemplate="<b>%{text}</b><br>Defunciones: %{z}<extra></extra>",
    marker_opacity=0.85,
    marker_line_width=0.3
))
fig_mapa.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=4.2,
    mapbox_center={"lat": 4.5709, "lon": -74.2973},
    margin={"r":10, "t":50, "l":10, "b":10},
    title=dict(text="Distribución geográfica del total de muertes (2019)", font=dict(color=colores['oscuro'], size=18)),
    paper_bgcolor=colores['blanco'],
    plot_bgcolor=colores['blanco']
)

# 6.2 Gráfico de líneas (meses)
linea_data = df_completo.groupby('MES').size().reset_index(name='TOTAL')
fig_lineas = go.Figure()
fig_lineas.add_trace(go.Scatter(
    x=linea_data['MES'],
    y=linea_data['TOTAL'],
    mode='lines+markers',
    line=dict(color=colores['oscuro'], width=3),
    marker=dict(size=9, color=colores['medio'], symbol='circle')
))
fig_lineas.update_layout(
    title=dict(text="Evolución temporal: Muertes por mes", font=dict(color=colores['oscuro'])),
    xaxis_title="Mes calendario",
    yaxis_title="Cantidad total de defunciones",
    paper_bgcolor=colores['blanco'],
    plot_bgcolor=colores['blanco'],
    xaxis=dict(tickmode='linear', dtick=1),
    hovermode="x unified"
)

# 6.3 Gráfico de barras top 5 (X95)
df_homicidios = df_completo[df_completo['CODIGO_3'] == 'X95']
barras_data = df_homicidios.groupby('MUNICIPIO').size().reset_index(name='CASOS')
barras_data = barras_data.sort_values(by='CASOS', ascending=False).head(5)
fig_barras = go.Figure(data=[go.Bar(
    x=barras_data['MUNICIPIO'],
    y=barras_data['CASOS'],
    marker_color=colores['medio'],
    text=barras_data['CASOS'],
    textposition='auto',
    width=0.6
)])
fig_barras.update_layout(
    title=dict(text="Top 5 ciudades: Homicidios por arma de fuego (X95)", font=dict(color=colores['oscuro'])),
    xaxis_title="Municipio",
    yaxis_title="Número de Homicidios",
    paper_bgcolor=colores['blanco'],
    plot_bgcolor=colores['blanco']
)

# 6.4 Gráfico circular top 10 menor índice
circular_data = df_completo.groupby('MUNICIPIO').size().reset_index(name='TOTAL')
circular_data = circular_data.sort_values(by='TOTAL', ascending=True).head(10)
fig_circular = go.Figure(data=[go.Pie(
    labels=circular_data['MUNICIPIO'],
    values=circular_data['TOTAL'],
    hole=0.5,
    marker=dict(colors=[colores['oscuro'], colores['medio'], colores['claro'], '#4F6C8A', '#80A4C2']),
    textinfo='label+percent',
    hoverinfo='label+value'
)])
fig_circular.update_layout(
    title=dict(text="10 ciudades con menor registro absoluto de mortalidad", font=dict(color=colores['oscuro'])),
    paper_bgcolor=colores['blanco'],
    plot_bgcolor=colores['blanco'],
    showlegend=False
)

# 6.5 Tabla top 10 causas de muerte
tabla_data = df_completo.groupby('CAUSA_MUERTE').size().reset_index(name='CASOS')
tabla_data = tabla_data.sort_values(by='CASOS', ascending=False).head(10)
fig_tabla = go.Figure(data=[go.Table(
    header=dict(
        values=['Causa clínica', 'Número de casos'],
        fill_color=colores['oscuro'],
        font=dict(color=colores['blanco'], size=13),
        align='left',
        height=35
    ),
    cells=dict(
        values=[tabla_data['CAUSA_MUERTE'], tabla_data['CASOS']],
        fill_color=[colores['claro'], colores['blanco']],
        font=dict(color=colores['texto'], size=12),
        align='left',
        height=30
    )
)])
fig_tabla.update_layout(
    title=dict(text="Escalafón de las 10 principales causas clínicas de muerte", font=dict(color=colores['oscuro'])),
    margin=dict(t=50, b=10, l=10, r=10),
    paper_bgcolor=colores['blanco']
)

# 6.6 Barras apiladas por sexo y departamento
apiladas_data = df_completo.groupby(['DEPARTAMENTO', 'SEXO']).size().unstack(fill_value=0).reset_index()
fig_apiladas = go.Figure()
if 'Masculino' in apiladas_data.columns:
    fig_apiladas.add_trace(go.Bar(
        x=apiladas_data['DEPARTAMENTO'],
        y=apiladas_data['Masculino'],
        name='Masculino',
        marker_color=colores['oscuro']
    ))
if 'Femenino' in apiladas_data.columns:
    fig_apiladas.add_trace(go.Bar(
        x=apiladas_data['DEPARTAMENTO'],
        y=apiladas_data['Femenino'],
        name='Femenino',
        marker_color=colores['claro']
    ))
fig_apiladas.update_layout(
    barmode='stack',
    title=dict(text="Sobremortalidad y composición por sexo departamental", font=dict(color=colores['oscuro'])),
    xaxis_title="Departamento registrado",
    yaxis_title="Volumen absoluto",
    paper_bgcolor=colores['blanco'],
    plot_bgcolor=colores['blanco'],
    xaxis=dict(tickangle=-45)
)

# 6.7 Histograma edades
orden_edades = ['Mortalidad neonatal', 'Mortalidad infantil', 'Primera infancia', 'Niñez', 'Adolescencia', 
                'Juventud', 'Adultez temprana', 'Adultez intermedia', 'Vejez', 'Longevidad / Centenarios', 'Edad desconocida']
hist_data = df_completo['CATEGORIA_EDAD'].value_counts().reindex(orden_edades).fillna(0).reset_index()
hist_data.columns = ['Categoria', 'Cantidad']
fig_hist = go.Figure(data=[go.Bar(
    x=hist_data['Categoria'],
    y=hist_data['Cantidad'],
    marker_color=colores['medio'],
    opacity=0.9
)])
fig_hist.update_layout(
    title=dict(text="Volumen de mortalidad por etapas del ciclo vital", font=dict(color=colores['oscuro'])),
    xaxis_title="Rango etario",
    yaxis_title="Densidad de casos",
    paper_bgcolor=colores['blanco'],
    plot_bgcolor=colores['blanco'],
    xaxis=dict(tickangle=-45)
)

# 7. INICIALIZACIÓN Y DISEÑO (LAYOUT)
app = Dash(__name__)
server = app.server

app.layout = html.Div(style={'backgroundColor': '#F8F9FA', 'padding': '30px', 'fontFamily': 'Helvetica, Arial, sans-serif'}, children=[
    html.Div(style={'backgroundColor': colores['oscuro'], 'padding': '25px', 'borderRadius': '12px', 'textAlign': 'center', 'marginBottom': '40px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'}, children=[
        html.H1("Mortalidad en Colombia (2019) - UNISALLE 2026", style={'color': colores['blanco'], 'letterSpacing': '1px', 'fontSize': '28px', 'margin': '0'}),
        html.P("Exploración interactiva de estadísticas vitales, violencia y causas clínicas", style={'color': colores['claro'], 'fontSize': '16px', 'marginTop': '10px'}),
    html.A(
            "Ver repositorio en GitHub",
            href="https://github.com/rmhzo77/dashboard-mortalidad-col-rmhzo.git", # Coloca tu enlace real aquí
            target="_blank",
            style={
                'display': 'inline-block',
                'marginTop': '20px',
                'padding': '10px 24px',
                'backgroundColor': colores['blanco'],
                'color': colores['oscuro'],
                'textDecoration': 'none',
                'fontWeight': 'bold',
                'fontFamily': 'Helvetica, Arial, sans-serif',
                'borderRadius': '8px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'
            }
        )
    ]),
    
    # Cuadrícula responsiva
    html.Div(className="grid-container", children=[
        html.Div(className="grid-item full-width", children=[dcc.Graph(figure=fig_mapa)]),
        html.Div(className="grid-item", children=[dcc.Graph(figure=fig_lineas)]),
        html.Div(className="grid-item", children=[dcc.Graph(figure=fig_barras)]),
        html.Div(className="grid-item", children=[dcc.Graph(figure=fig_circular)]),
        html.Div(className="grid-item", children=[dcc.Graph(figure=fig_apiladas)]),
        html.Div(className="grid-item full-width", children=[dcc.Graph(figure=fig_hist)]),
        html.Div(className="grid-item full-width", children=[dcc.Graph(figure=fig_tabla)])
    ]),
    
    html.Div(style={'textAlign': 'center', 'marginTop': '40px', 'color': colores['medio'], 'fontSize': '14px'}, children=[
        html.P("Desarrollo académico - Rodrigo Madera Herazo - Fuente: Datos abiertos (DANE)")
    ])
])

# INSTRUCCIÓN DE ARRANQUE LOCAL
if __name__ == '__main__':
    app.run_server(debug=True)

