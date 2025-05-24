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
    url = "https://docs.google.com/spreadsheets/d/16LxoNFY-rwmJh6adZ1_ByV4im8k_T__i/edit?usp=sharing&ouid=104676576460693310333&rtpof=true&sd=true"
    path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
    #path = 'user_behavior_dataset.csv'
    df = pd.read_excel(path)
    return df

df = load_data()

# Lista de países con 'Todos' al inicio
paises = ['Todos'] + sorted(df["País/Región"].unique())

# Filtro en cuerpo principal
pais_seleccionado = st.selectbox(
    "Selecciona un país/región",
    options=paises,
)

# Filtrar datos según selección
if pais_seleccionado == 'Todos':
    df_filtered = df
else:
    df_filtered = df[df["País/Región"] == pais_seleccionado]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("💰 Ventas totales", f"${df_filtered['Ventas'].sum():,.0f}")
col2.metric("📈 Ganancia total", f"${df_filtered['Ganancia'].sum():,.0f}")
col3.metric("👥 Número de clientes", df_filtered["Nombre del cliente"].nunique())

# Primera fila: tres gráficos
colv1, colv2, colv3 = st.columns([1,1,1])

with colv1:
    st.markdown("### Ventas por Categoría")
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
        color_discrete_sequence=['#F1C6D2'],
    )
    fig_cat.update_layout(
        yaxis=dict(tickformat=',d'),
        xaxis_tickangle=-45,
        margin=dict(t=40, b=100)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with colv2:
    st.markdown("### Ventas por Subcategoría")
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
        color_discrete_sequence=['#F1C6D2'],
    )
    fig_subcat.update_layout(
        xaxis=dict(tickformat=',d'),
        margin=dict(l=150, t=40, b=40),
    )
    st.plotly_chart(fig_subcat, use_container_width=True)

with colv3:
    st.markdown("### Ventas por Segmento")
    ventas_por_segmento = (
        df_filtered.groupby('Segmento')['Ventas']
        .sum()
        .sort_values(ascending=False)
    )

    fig_donut = px.pie(
        names=ventas_por_segmento.index,
        values=ventas_por_segmento.values,
        hole=0.5,
        color_discrete_sequence=['#D94F6D', '#F1C6D2', '#6E6E6E']
    )

    fig_donut.update_traces(textinfo='none', hovertemplate='%{label}<br>Ventas: %{value:,}<extra></extra>')
    fig_donut.update_layout(
        showlegend=True,
        margin=dict(t=40, b=40, l=40, r=40)
    )

    st.plotly_chart(fig_donut, use_container_width=True)

# Segunda fila: línea temporal y treemap
colm1, colm2 = st.columns([2,1])

with colm1:
    st.markdown("### Ventas y Ganancia Mensuales")
    df_mensual = df_filtered.groupby('mes_pedido')[['Ventas', 'Ganancia']].sum().sort_index()

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_mensual.index,
        y=df_mensual['Ventas'],
        mode='lines+markers',
        name='Ventas',
        line=dict(color='#6E6E6E')
    ))
    fig_line.add_trace(go.Scatter(
        x=df_mensual.index,
        y=df_mensual['Ganancia'],
        mode='lines+markers',
        name='Ganancia',
        line=dict(color='#D94F6D')
    ))
    fig_line.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        ),
        yaxis=dict(separatethousands=True),
        legend=dict(y=0.99, x=0.01),
        margin=dict(l=40, r=40, t=80, b=40),
        hovermode='x unified',
    )
    st.plotly_chart(fig_line, use_container_width=True)

with colm2:
    st.markdown("### Ventas por Método de Envío")
    ventas_por_envio = df_filtered.groupby('Método de envío')['Ventas'].sum().reset_index()

    fig_envio = px.treemap(
        ventas_por_envio,
        path=['Método de envío'],
        values='Ventas',
        color='Ventas',
        color_continuous_scale=['#F1C6D2', '#D94F6D', '#6E6E6E'],
        hover_data={'Ventas': ':,.0f'}
    )
    fig_envio.update_layout(margin=dict(t=50, b=50, l=50, r=50))
    st.plotly_chart(fig_envio, use_container_width=True)

# Conclusión
st.markdown("*Realizado por Martha Rugeles y Camila Gallego*")