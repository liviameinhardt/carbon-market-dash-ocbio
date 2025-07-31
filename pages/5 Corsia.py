import os
import streamlit as st  
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc

from utils import components as c

############################## Configurações da página (inicio) ##############################
c.pag_config(os.path.basename(__file__))
c.sobre_dash()
############################## Configurações da página (fim) ##############################


st.title("CORSIA")
st.write("Fontes: CORSIA (2024); Ecosystem Marketplace (2022)")
st.markdown("##") #espacamento entre blocos

#carregar os dados
corsia_countries = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="CORSIA_countries")
corsia_precos = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="CORSIA_price",index_col=0)
iso_countries = pd.read_csv("data/processed/iso_countries.csv", sep=";", decimal=",", index_col=1)

#dado manual (nao foi traduzido no excel)
traducao_setores = {
    "Energy Efficiency /Fuel Switching": "Eficiência Energética / Troca de Combustível",
    "Forestry and Land Use": "Florestas e Uso da Terra",
    "Renewable Energy": "Energia Renovável",
    "Waste Disposal": "Descarte de Resíduos",
    "Other": "Outros"
}

corsia_precos.columns = corsia_precos.columns.str.strip().map(traducao_setores)

#get ISO country codes
corsia_countries['country'] = corsia_countries['country'].str.strip()
corsia_countries = corsia_countries.join(iso_countries, on="country", how="left")

initial_year = corsia_countries.groupby(["ISO","country"])['year'].agg(["min","max"])

paises_nao_participantes = initial_year[initial_year['max'] != corsia_countries['year'].max()].copy()\
                        .reset_index().drop("ISO", axis=1)\
                        .rename(columns={"min":"Ano de Entrada","max":"Ano de Saída","country":"País"})\
                        .set_index("País")

initial_year = initial_year[initial_year["max"]==corsia_countries['year'].max()].reset_index().sort_values("min")
initial_year['min'] = initial_year['min'].astype(str)


######### gráfico mapa #########

filtro, grafico = st.columns([1, 3], gap="large")

with filtro:
    modo = st.radio("Modo de visualização", 
                    ("Por ano", f"Total {corsia_countries['year'].max()}, por ano de entrada"))

with grafico:

    # Define a paleta de cores
    n = len(initial_year['min'].unique())+1
    blue_shades = pc.sample_colorscale("Blues", [i / (n - 1) for i in range(n)])[1:]

    if modo == "Por ano":
        
        select_year = filtro.selectbox("Selecione o ano", corsia_countries['year'].unique()[::-1], index=0)
        cur_year = corsia_countries[corsia_countries['year'] == select_year].copy()

        #plot map
        fig = px.choropleth(cur_year, 
                            locations="ISO", 
                            # color="year",
                            hover_name="country",
                            # hover_data={i:False for i in initial_year.columns},
                            labels={'year': 'Ano de Entrada'},
                            color_discrete_sequence=blue_shades)
        
        fig.update_layout(
            title=dict(text=f"Países participantes do CORSIA | {select_year}", font=dict(size=20),),
                width=800,
                height=500,
                margin=dict(b=0),
                showlegend=False,
        )

    else:

        fig = px.choropleth(initial_year, 
                        locations="ISO", 
                        color="min",
                        hover_name="country",
                        hover_data={i:False for i in initial_year.columns},
                        labels={'min': 'Ano de Entrada',},
                        color_discrete_sequence=blue_shades)


        fig.update_layout(
            title=dict(text=f"Países participantes do CORSIA | {initial_year['min'].min()} - {initial_year['max'].max()}", font=dict(size=20),),
                 width=800,
                height=500,
                margin=dict(b=0),
                showlegend=True,
                legend=dict(
                    orientation="v",x=0,xanchor="center",
                    y=1,yanchor="auto", font=dict(size=15)
                ),
    
        )

    fig.update_geos(showocean=True, oceancolor="#F2F2F2", showcountries=True,
                        showland=True, landcolor="#F2F2F2",)

    st.plotly_chart(fig, use_container_width=True)

#legenda por fora do da coluna para ocupar o espaço todo
st.caption("O mapa apresenta os países participantes do CORSIA (Carbon Offsetting and Reduction Scheme for International Aviation), conforme o ano de adesão ao mecanismo. A visualização permite dois modos de consulta: (i) por ano específico, destacando os países que participaram em determinado ano; e (ii) total acumulado até 2025, indicando o ano de entrada de cada país no programa.")

# numero de participantes por ano #
col1, col2 = st.columns(2)
participantes_por_ano = corsia_countries.groupby("year")['ISO'].count()

fig = px.bar(participantes_por_ano,
                x=participantes_por_ano.index,
                y=participantes_por_ano.values,
                text_auto=True,
                labels={'year':'Ano','y':'Número de países'},
                title="Número de Países Participantes do CORSIA por Ano",
                )

col1.plotly_chart(fig, use_container_width=True)
col1.caption("O gráfico apresenta a evolução anual do número de países participantes do CORSIA")

col2.markdown("<b>Países que saíram do CORSIA</b>",unsafe_allow_html=True)
col2.table(paises_nao_participantes)
col2.caption("A tabela indica os países que deixaram de participar do programa, com os respectivos anos de entrada e saída.")

# CORSIA preços
fig = px.bar(corsia_precos.T, 
                barmode="group",
                text_auto=True,
                labels={'index':'Escopo','value':'USD/tCO2eq','Year':'Ano'},
                title="Preço dos Créditos de Carbono Elegíveis para CORSIA | por Ano e Escopo",
                )

st.plotly_chart(fig, use_container_width=True)
st.caption("O gráfico apresenta os preços médios (em US$/tCO₂eq) dos créditos de carbono elegíveis para uso no CORSIA, desagregados por categoria de projeto e ano (2020 e 2021)")
