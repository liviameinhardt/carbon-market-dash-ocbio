import os
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import graficos as g
from utils import components as c

############################## Configurações da página (inicio) ##############################
c.pag_config(os.path.basename(__file__))
c.sobre_dash()
############################## Configurações da página (fim) ##############################

st.title("Mercados Regulados")
st.text("Fonte: Banco Mundial (Abril, 2024)")  

# Carregar os dados
data_wb = pd.read_csv("data/processed/wb_info.csv",sep=";",decimal=",")
series_wb = pd.read_csv("data/processed/wb_time_series.csv",sep=";",decimal=",")
iso = pd.read_csv("data/processed/iso_countries.csv", on_bad_lines='skip',delimiter=';',index_col=1)

data_wb = data_wb[data_wb["Type"]=="Sistema  de comércio de licenças de emissão (ETS)"]
series_wb =series_wb[series_wb["Instrument Type"]=="ETS"]

# METRICAS (RESUMO)

# iniciativas implementadas
implementadas = data_wb[data_wb["Status"]=="Implementado"].copy()
iniciativas_implementadas = len(implementadas["Instrument name"].unique())
iniciativas_anteriores = len(implementadas[implementadas["Start Year"]<implementadas["Start Year"].max()]["Instrument name"].unique())
crescimento_iniciativas = iniciativas_implementadas - iniciativas_anteriores

# % emissoes globais cobertas
percent_emissoes = sum(data_wb["Share of global emissions covered"].dropna())*100
percent_emissoes_ano_anterior = sum(data_wb[data_wb["Start Year"]<data_wb["Start Year"].max()]["Share of global emissions covered"].dropna())*100
crescimento_percent_emissoes = percent_emissoes - percent_emissoes_ano_anterior


# preço medio
preco_medio = series_wb[series_wb["Year"]==series_wb["Year"].max()]["Price"].dropna().mean()
preco_medio_ano_anterior = series_wb[series_wb["Year"]==series_wb["Year"].max()-1]["Price"].dropna().mean()
crescimento_preco_medio = preco_medio - preco_medio_ano_anterior

#receita média 
receita_medio = series_wb[series_wb["Year"]==series_wb["Year"].max()-1]["Revenue"].dropna().mean()
receita_medio_ano_anterior = series_wb[series_wb["Year"]==series_wb["Year"].max()-2]["Revenue"].dropna().mean()
crescimento_receita_medio = receita_medio - receita_medio_ano_anterior

metrics_col = st.columns(4)
metrics_col[0].metric(f"Iniciativas Implementadas", iniciativas_implementadas, f"{crescimento_iniciativas}", border=True,help="Variação em relação ao ano anterior abaixo.")
metrics_col[1].metric("Percentual de emissões globais cobertas", f"{percent_emissoes:.2f}%",delta=f"{crescimento_percent_emissoes:.2f}%", border=True,help="Variação em relação ao ano anterior abaixo.")
metrics_col[2].metric("Preço médio (US$/tCO2e)", f"${preco_medio:.2f}", delta=f"{crescimento_preco_medio:.2f} USD", border=True,help="Variação em relação ao ano anterior abaixo.")
metrics_col[3].metric("Receita média (Milhões US$)", f"${receita_medio:.2f}", delta=f"{crescimento_receita_medio:.2f} USD", border=True, delta_color="normal",help="Variação em relação ao ano anterior abaixo.")


 
st.markdown("##") #espacamento entre blocos 
# MAPA DO STATUS

#nacionais 
national = data_wb[data_wb["Subtype"]=="Nacional"].copy()
national["iso_alpha"] = national["Jurisdiction covered"].map(iso["ISO"].to_dict())

fig = px.choropleth(national, color="Status",
                    locations="iso_alpha", hover_data=["Jurisdiction covered"],
                     projection="equirectangular", labels={"Status":"Nacional"},
                     color_discrete_sequence=px.colors.qualitative.Pastel2,
                 )

# marcado para os estados/províncias
colors = px.colors.qualitative.Dark2
subnational = data_wb[data_wb["Subtype"]=="Subnacional - Estado/Província"].copy()
class_color_map = {cls: colors[i % len(colors)] for i, cls in enumerate(subnational["Status"].unique())}

#adiciona uma cor para cada status
for status in subnational["Status"].unique():

    cur_points = subnational[subnational["Status"]==status] 

    fig.add_trace(go.Scattergeo(
        lon=cur_points["lon"],
        lat=cur_points["lat"],
        text=cur_points["Instrument name"],
        mode="markers",
        marker=dict( size=12, color=class_color_map[status], opacity=0.7,symbol = 'square'),
        name = status,
        legendgroup="group2",
        legendgrouptitle_text="Subnacional - Estado/Província",
    ))

# marcado para os municípios
subnational = data_wb[data_wb["Subtype"]=="Subnacional - Município"].copy()
class_color_map = {cls: colors[i % len(colors)] for i, cls in enumerate(subnational["Status"].unique())}

#adiciona uma cor para cada status
for status in subnational["Status"].unique():

    cur_points = subnational[subnational["Status"]==status] 

    fig.add_trace(go.Scattergeo(
        lon=cur_points["lon"],
        lat=cur_points["lat"],
        text=cur_points["Instrument name"],
        mode="markers",
        marker=dict( size=9, color=class_color_map[status], opacity=0.7),
        name = status,
        legendgroup="group3",
        legendgrouptitle_text="Subnacional - Município",
    ))

# altera o layout do mapa
fig.update_geos(showocean=True, oceancolor="#F2F2F2", showcountries=True,
                    showland=True, landcolor="#F2F2F2",)

fig.update_layout(

    plot_bgcolor = "#F2F2F2",
    paper_bgcolor = "#F2F2F2",
    
    title=dict(text="Status - Mercados Regulados", font=dict(size=24),),
    
        width=800,
        height=500,
        margin=dict(b=0),

        showlegend=True,
        legend=dict(
            orientation="v",x=0,xanchor="right",
            y=0.9,yanchor="auto", font=dict(size=14)
        ),

    )


st.plotly_chart(fig, use_container_width=True)
st.caption("O mapa apresenta o status de implementação de ETS em diferentes jurisdições ao redor do mundo. As áreas coloridas representam iniciativas em nível nacional, enquanto os quadrados sobrepostos indicam políticas subnacionais (estaduais ou provinciais). Cada cor corresponde a um status distinto: implementado, em consideração, em desenvolvimento ou abolido; **ETS Regionais (EU, EU 27+) foram otimidos do mapa.**")

 
st.markdown("##") #espacamento entre blocos
st.header("Séries Históricas")
agregadas, por_iniciativa =  st.tabs(["Agregadas", "Por Iniciativa"])


with agregadas:

    preco, emissoes, receita = st.columns(3)

    g.serie_preco_agg(series_wb,key='agg', st_location=preco,tipo_mercado='ETS')
    g.serie_emissoes_agg(series_wb, emissoes,tipo_mercado='ETS')
    g.serie_receita_agg(series_wb, key='agg', st_location= receita,tipo_mercado='ETS')

    preco.caption("O gráfico apresenta a evolução histórica dos preços das iniciativas de ETS ao longo do tempo. A visualização permite diferentes métricas (média, mediana, mínimo e máximo), e pode ser consultada de forma agregada ou desagregada por iniciativa")
    emissoes.caption("Este gráfico mostra o percentual global de emissões de gases de efeito estufa coberto por iniciativas de ETS ao longo do tempo. A série histórica pode ser visualizada de forma agregada ou por iniciativa individual.")
    receita.caption("O gráfico apresenta a evolução  da receita anual gerada por  iniciativas de ETS. A visualização permite  consulta de forma agregada ou  desagregada por iniciativa.")


with por_iniciativa:


    iniciativas = st.multiselect("Iniciativas",
                                options=series_wb["Name of the initiative"].unique(),
                                default=series_wb["Name of the initiative"].unique()[10],
                )
    
    cur_selection = series_wb[series_wb["Name of the initiative"].isin(iniciativas)].copy()

    preco, emissoes, receita = st.columns(3)

    g.compare_series_plot(cur_selection, "Price",legend_name="Name of the initiative", st_location=preco,tipo_mercado='ETS')
    g.compare_series_plot(cur_selection, "Revenue",legend_name="Name of the initiative", st_location=receita,tipo_mercado='ETS')
    g.compare_series_plot(cur_selection, "Emissions",legend_name="Name of the initiative", st_location=emissoes,tipo_mercado='ETS')

    
    preco.caption("O gráfico apresenta a evolução histórica dos preços das iniciativas de ETS ao longo do tempo. A visualização permite diferentes métricas (média, mediana, mínimo e máximo), e pode ser consultada de forma agregada ou desagregada por iniciativa")
    emissoes.caption("Este gráfico mostra o percentual global de emissões de gases de efeito estufa coberto por iniciativas de ETS ao longo do tempo. A série histórica pode ser visualizada de forma agregada ou por iniciativa individual.")
    receita.caption("O gráfico apresenta a evolução  da receita anual gerada por  iniciativas de ETS. A visualização permite  consulta de forma agregada ou  desagregada por iniciativa.")
