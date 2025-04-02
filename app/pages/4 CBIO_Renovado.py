import streamlit as st  
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config (
    page_title="CBIO Renovado",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("CBIO Renovado")
st.write("Fonte: B3 (Março, 2025)")

cbio_data = pd.read_csv("../data/processed/cbio_data.csv",sep=";",decimal=",",index_col=0)
cbio_data.index = pd.to_datetime(cbio_data.index)

cbio_negociacoes = pd.read_csv("../data/processed/cbio_negociacoes.csv",sep=";",decimal=",",index_col=0)
cbio_negociacoes.index = pd.to_datetime(cbio_negociacoes.index)
cbio_negociacoes.rename(columns={"Valor Financeiro":"Receita"}, inplace=True)

freq_dict = {False:"Diário", "M":"Mensal", "Q":"Trimestral", "Y":"Anual"}

freq = st.sidebar.radio("Agregação", (False,"M", "Q", "Y"), index=1, horizontal=True,
                format_func=lambda x: freq_dict[x]) # Use format_func to replace spaces with underscores and convert to lowercase

if freq:
    cbio_data  = cbio_data.groupby(pd.Grouper(freq=freq)).sum()
    cbio_negociacoes = cbio_negociacoes.drop(["Ativo","Liquidação"],axis=1).astype(float).groupby(pd.Grouper(freq=freq)).mean()


fig = go.Figure()
fig.add_trace(go.Scatter(x=cbio_data.index, y=cbio_data["Aposentadoria"], mode='lines', name='Aposentadoria'))
fig.add_trace(go.Scatter(x=cbio_data.index, y=cbio_data["Estoque"], mode='lines', name='Estoque',yaxis='y2'))

fig.update_layout(title=f"Créditos de Descarbonização (CBIO) Negociados e Aposentados <br><sup>{cbio_data.index[0].date()} - {cbio_data.index[-1].date()}<sup>",
                    yaxis2=dict( overlaying='y', side='right'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1))

st.plotly_chart(fig, use_container_width=True)


# cbio_negociacoes

preco, receita = st.columns(2)

with preco:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cbio_negociacoes.index, y=cbio_negociacoes["Preço Médio"], mode='lines', name='Medio'))

    fig.update_layout(title=f"Preço Médio {freq_dict[freq]} (R$) <br><sup>{cbio_negociacoes.index[0].date()} - {cbio_negociacoes.index[-1].date()}<sup>",
                        yaxis2=dict( overlaying='y', side='right'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1))

    st.plotly_chart(fig, use_container_width=True)

with receita:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cbio_negociacoes.index, y=cbio_negociacoes["Receita"], mode='lines', name='Receita (R$)'))

    fig.update_layout(title=f"Receita Média {freq_dict[freq]} (R$) <br><sup>{cbio_negociacoes.index[0].date()} - {cbio_negociacoes.index[-1].date()}<sup>",
                        yaxis2=dict( overlaying='y', side='right'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1))

    st.plotly_chart(fig, use_container_width=True)

# if not freq:
grafico, filtro = st.columns([5,2])

data = cbio_negociacoes.join(cbio_data)

with filtro:

    xaxis = st.selectbox("Eixo X", data.columns, index=0)
    yaxis = st.selectbox("Eixo Y", data.drop(xaxis,axis=1).columns, index=2)

with grafico:
    
    fig = px.scatter(data, x=xaxis, y=yaxis, 
                     title=f"Relação entre {xaxis} e {yaxis} <br><sup>{data.index[0].date()} - {data.index[-1].date()}<sup>")
    
    st.plotly_chart(fig, use_container_width=True)


