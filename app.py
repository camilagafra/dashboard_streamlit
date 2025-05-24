import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración inicial
st.set_page_config(page_title="Dashboard Ventas Minorista", layout="wide")
st.title("📈 Panel Estratégico de Ventas y Comportamiento")

# Cargar datos
@st.cache_data
def load_data():
    url = "https://drive.google.com/file/d/1iS3w5ANLEyYeS3piOqDBjL1rPIMi1VSv/view?usp=sharing"
    path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
    #path = 'user_behavior_dataset.csv'
    df = pd.read_csv(path, sep=',')
    df["Fecha del pedido"] = pd.to_datetime(df["Fecha del pedido"]) 
    return df

df = load_data()

# Sidebar filtros
st.sidebar.header("Filtros")

pais_filter = st.sidebar.multiselect(
    "País/Región",
    options=df["País/Región"].unique(),
    default=df["País/Región"].unique()
)

categoria_filter = st.sidebar.multiselect(
    "Categoría",
    options=df["Categoría"].unique(),
    default=df["Categoría"].unique()
)

segmento_filter = st.sidebar.multiselect(
    "Segmento",
    options=df["Segmento"].unique(),
    default=df["Segmento"].unique()
)

fecha_min = df["Fecha del pedido"].min()
fecha_max = df["Fecha del pedido"].max()

fecha_range = st.sidebar.date_input(
    "Rango de fechas del pedido",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtrar datos
df_filtered = df[
    (df["País/Región"].isin(pais_filter)) &
    (df["Categoría"].isin(categoria_filter)) &
    (df["Segmento"].isin(segmento_filter)) &
    (df["Fecha del pedido"] >= pd.to_datetime(fecha_range[0])) &
    (df["Fecha del pedido"] <= pd.to_datetime(fecha_range[1]))
]

# KPIs arriba en 3 columnas
col1, col2, col3 = st.columns(3)
col1.metric("💰 Ventas totales", f"${df_filtered['Ventas'].sum():,.0f}")
col2.metric("📈 Ganancia total", f"${df_filtered['Ganancia'].sum():,.0f}")
col3.metric("👥 Número de clientes únicos", df_filtered["Nombre del cliente"].nunique())

# --- Primera fila con 3 gráficos ---
colv1, colv2, colv3 = st.columns([1,1,1])

with colv1:
    ventas_por_categoria = (
        df_filtered.groupby('Categoría')['Ventas']
        .sum()
        .reset_index()
        .sort_values(by='Ventas', ascending=False)
    )
    fig_cat = px.bar(
        ventas_por_categoria,
        x='Categoría',
        y='Ventas',
        title='Ventas Totales por Categoría de Producto',
        text=ventas_por_categoria['Ventas'].apply(lambda x: f'{int(x):,}'),
        color_discrete_sequence=['#F1C6D2'],
    )
    fig_cat.update_traces(textposition='outside')
    fig_cat.update_layout(
        yaxis=dict(title='Ventas Totales', tickformat=',d'),
        xaxis=dict(title='Categoría de Producto'),
        xaxis_tickangle=-45,
        margin=dict(t=40, b=100)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with colv2:
    subcat_ventas_ganancia = (
        df_filtered.groupby('Subcategoría')[['Ventas', 'Ganancia']]
        .sum()
        .reset_index()
    )
    ventas_ordenadas = subcat_ventas_ganancia.sort_values(by='Ventas', ascending=True)
    fig_subcat = px.bar(
        ventas_ordenadas,
        y='Subcategoría',
        x='Ventas',
        orientation='h',
        title='Ventas Totales por Subcategoría',
        text=ventas_ordenadas['Ventas'].apply(lambda x: f'{int(x):,}'),
        color_discrete_sequence=['#F1C6D2'],
    )
    fig_subcat.update_traces(textposition='outside')
    fig_subcat.update_layout(
        xaxis=dict(title='Ventas Totales', tickformat=',d'),
        yaxis=dict(title='Subcategoría'),
        margin=dict(l=150, t=40, b=40),
    )
    st.plotly_chart(fig_subcat, use_container_width=True)

with colv3:
    # Mapa con ventas por país
    ventas_pais = (
        df_filtered.groupby('País/Región')['Ventas']
        .sum()
        .reset_index()
        .sort_values(by='Ventas', ascending=False)
        .head(10)
    )
    
    fig_map = px.choropleth(
        ventas_pais,
        locations='País/Región',
        locationmode='country names',
        color='Ventas',
        color_continuous_scale='Blues',
        title='Top 10 Países por Ventas',
        hover_data={'Ventas':':,.0f'},
    )
    fig_map.update_layout(margin=dict(t=50, b=0, l=0, r=0))
    st.plotly_chart(fig_map, use_container_width=True)

# --- Segunda fila: línea evolución mensual y pie charts ---
colm1, colm2 = st.columns([2,1])

with colm1:
    df_mensual = df_filtered.groupby('mes_pedido')[['Ventas', 'Ganancia']].sum().sort_index()

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_mensual.index,
        y=df_mensual['Ventas'],
        mode='lines+markers+text',
        name='Ventas',
        text=[f"{int(v):,}" for v in df_mensual['Ventas']],
        textposition='top center',
        line=dict(color='#6E6E6E')
    ))
    fig_line.add_trace(go.Scatter(
        x=df_mensual.index,
        y=df_mensual['Ganancia'],
        mode='lines+markers+text',
        name='Ganancia',
        text=[f"{int(v):,}" for v in df_mensual['Ganancia']],
        textposition='bottom center',
        line=dict(color='#D94F6D')
    ))
    fig_line.update_layout(
        title='Evolución Mensual de Ventas y Ganancias',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            title='Mes del Año'
        ),
        yaxis=dict(
            title='Monto Total',
            separatethousands=True
        ),
        legend=dict(y=0.99, x=0.01),
        margin=dict(l=40, r=40, t=80, b=40),
        hovermode='x unified',
    )
    st.plotly_chart(fig_line, use_container_width=True)

with colm2:
    colores_personalizados = ['#6E6E6E', '#D94F6D', '#F1C6D2', '#A9A9A9', '#2A9D8F']

    ventas_por_envio = df_filtered.groupby('Método de envío')['Ventas'].sum().sort_values(ascending=False)
    fig_envio = go.Figure(data=[go.Pie(
        labels=ventas_por_envio.index,
        values=ventas_por_envio.values,
        hole=0,
        marker=dict(colors=colores_personalizados[:len(ventas_por_envio)]),
        hovertemplate='%{label}<br>Cantidad: %{value:,}<br>Porcentaje: %{percent}',
        textinfo='label+percent'
    )])
    fig_envio.update_layout(title='Distribución de Ventas por Método de Envío', margin=dict(t=50, b=50, l=50, r=50))
    st.plotly_chart(fig_envio, use_container_width=True)

    ventas_por_segmento = df_filtered.groupby('Segmento')['Ventas'].sum().sort_values(ascending=False)
    fig_segmento = go.Figure(data=[go.Pie(
        labels=ventas_por_segmento.index,
        values=ventas_por_segmento.values,
        hole=0.3,
        marker=dict(colors=colores_personalizados[:len(ventas_por_segmento)]),
        hovertemplate='%{label}<br>Cantidad: %{value:,}<br>Porcentaje: %{percent}',
        textinfo='label+percent'
    )])
    fig_segmento.update_layout(title='Ventas Totales por Segmento de Cliente', margin=dict(t=50, b=50, l=50, r=50))
    st.plotly_chart(fig_segmento, use_container_width=True)

# Conclusiones
st.markdown("*Realizado por Martha Rugeles y Camila Gallego*")