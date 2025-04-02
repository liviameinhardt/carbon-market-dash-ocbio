#%%


import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import graficos as g

st.set_page_config (
    page_title="Taxa de Carbono",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Taxa de Carbono")
st.text("Fonte: Banco Mundial (Abril, 2024)")  #automatico (criar um info.txt)
st.markdown("##")

# Carregar os dados
data_wb = pd.read_csv("..\..\data\processed\wb_info.csv",sep=";",decimal=",")
series_wb = pd.read_csv("..\..\data\processed\wb_time_series.csv",sep=";",decimal=",")
iso = pd.read_csv("..\..\data\processed\iso_countries.csv", on_bad_lines='skip',delimiter=';',index_col=1)

data_wb = data_wb[data_wb["Type"]=="Carbon tax"]
series_wb =series_wb[series_wb["Instrument Type"]=="Carbon tax"]



# METRICAS (RESUMO)

# iniciativas implementadas
implementadas = data_wb[data_wb["Status"]=="Implemented"]
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
metrics_col[0].metric(f"Iniciativas Implementadas", iniciativas_implementadas, f"{crescimento_iniciativas}", border=True)
metrics_col[1].metric("Percentual de emissões globais cobertas", f"{percent_emissoes:.2f}%",delta=f"{crescimento_percent_emissoes:.2f}%", border=True)
metrics_col[2].metric("Preço médio (US$/tCO2e)", f"${preco_medio:.2f}", delta=f"{crescimento_preco_medio:.2f} USD", border=True)
metrics_col[3].metric("Receita média (Milhões US$)", f"${receita_medio:.2f}", delta=f"{crescimento_receita_medio:.2f} USD", border=True, delta_color="normal")

st.markdown("##")

# MAPA DO STATUS

#fill countries geo for national carbon tax
national = data_wb[data_wb["Subtype"]=="National"].copy()
national["iso_alpha"] = national["Jurisdiction covered"].map(iso["ISO"].to_dict())

fig = px.choropleth(national, color="Status",
                    locations="iso_alpha", hover_data=["Jurisdiction covered"],
                     projection="equirectangular", labels={"Status":"National"},
                 )

# add marker to subnational carbon tax 
subnational = data_wb[data_wb["Subtype"]=="Subnational - State/Province"].copy()

colors = px.colors.qualitative.T10
class_color_map = {cls: colors[i % len(colors)] for i, cls in enumerate(subnational["Status"].unique())}

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
        legendgrouptitle_text="Subnational (State/Province)",
    ))


fig.update_geos(fitbounds="locations", visible=False, showcountries=True)

fig.update_layout(

    title=dict(text="Status - Mercados de Taxa de Carbono", font=dict(size=20),),
        
        width=700,
        height=700,

        showlegend=True,
        legend=dict(
            orientation="v",x=0,xanchor="center",
            y=1,yanchor="auto", font=dict(size=15)
        ),

    )


st.plotly_chart(fig, use_container_width=True)

st.header("Séries Históricas")
agregadas, por_iniciativa =  st.tabs(["Agregadas", "Por Iniciativa"])


with agregadas:

    preco, emissoes, receita = st.columns(3)

    g.serie_preco_agg(series_wb,key='agg', st_location=preco,legend=False)
    g.serie_emissoes_agg(series_wb, emissoes,legend=False)
    g.serie_receita_agg(series_wb, key='agg', st_location= receita,legend=False)

with por_iniciativa:


    iniciativas = st.multiselect("Iniciativas",
                                options=series_wb["Name of the initiative"].unique(),
                                default=series_wb["Name of the initiative"].unique()[10],
                )
    
    cur_selection = series_wb[series_wb["Name of the initiative"].isin(iniciativas)].copy()

    preco, emissoes, receita = st.columns(3)

    g.compare_series_plot(cur_selection, "Price",legend_name="Name of the initiative", st_location=preco)
    g.compare_series_plot(cur_selection, "Revenue",legend_name="Name of the initiative", st_location=receita)
    g.compare_series_plot(cur_selection, "Emissions",legend_name="Name of the initiative", st_location=emissoes)
    
