#%%


import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import graficos as g


colors = px.colors.qualitative.T10

st.set_page_config (
    page_title="Sistema de Comércio de Emissões",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Sistema de Comércio de Carbono")
st.text("Fonte: Banco Mundial (Abril, 2024)")  #automatico (criar um info.txt)
st.markdown("##")

# Carregar os dados
data_wb = pd.read_csv("..\..\data\processed\wb_info.csv",sep=";",decimal=",")
series_wb = pd.read_csv("..\..\data\processed\wb_time_series.csv",sep=";",decimal=",")
iso = pd.read_csv("..\..\data\processed\iso_countries.csv", on_bad_lines='skip',delimiter=';',index_col=1)

data_wb = data_wb[data_wb["Type"]=="ETS"]
series_wb =series_wb[series_wb["Instrument Type"]=="ETS"]

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

# Subnational - State/Province
# National
# Subnational - City

# Regional
# National Undecided

#fill countries geo for national carbon tax
national = data_wb[data_wb["Subtype"]=="National"].copy()
national["iso_alpha"] = national["Jurisdiction covered"].map(iso["ISO"].to_dict())

fig = px.choropleth(national, color="Status",
                    locations="iso_alpha", hover_data=["Jurisdiction covered"],
                     projection="equirectangular", labels={"Status":"National"},
                 )

# add marker to subnational carbon tax 
subnational = data_wb[data_wb["Subtype"]=="Subnational - State/Province"].copy()
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

#add maerket to subnational (city)carbon tax
subnational = data_wb[data_wb["Subtype"]=="Subnational - City"].copy()
class_color_map = {cls: colors[i % len(colors)] for i, cls in enumerate(subnational["Status"].unique())}

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
        legendgrouptitle_text="Subnational (City)",
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
st.caption("ETS Regionais (EU, EU 27+) foram otimidos do mapa.")

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
    

st.markdown("##")
st.header("Principais Sistemas de Comércio de Emissões")
st.write("Fontes: Refinitiv  European Energy Exchange, California Air Resources Board, The regional greenhouse gas initiative")
st.markdown("##")

# Carregar os dados
eu_ets  = pd.read_excel("..\..\dataprocessed\DADOS_MANUAIS.xlsx", sheet_name="EU_ETS_Carbon_permits",index_col=0)
california_ets  = pd.read_excel("..\..\dataprocessed\DADOS_MANUAIS.xlsx", sheet_name="CaliforniaQuébec_Carbon",index_col=0)
china_ets = pd.read_excel("..\..\dataprocessed\DADOS_MANUAIS.xlsx", sheet_name="CHINA_ETS",index_col=0)
rggi_ets = pd.read_excel("..\..\dataprocessed\DADOS_MANUAIS.xlsx", sheet_name="RGGI_USD_Volume",index_col=0)

eu_ets.index = pd.to_datetime(eu_ets.index)
california_ets.index = pd.to_datetime(california_ets.index)
china_ets.index = pd.to_datetime(china_ets.index)
rggi_ets.index = pd.to_datetime(rggi_ets.index)

china_ets = china_ets.drop("China",axis=1).unstack().reset_index(level=0).rename(columns={"level_0":"State",0:"Price"}).dropna()

frequencia_dados = st.radio("Frequência dos dados", ["Original", "Trimestral","Anual"], index=0, key="freq",horizontal=True)

if frequencia_dados == "Trimestral": agg_freq="Q"
elif frequencia_dados == "Anual": agg_freq="Y"


europa, california = st.columns(2)
china, rggi = st.columns(2)


with europa:

    if frequencia_dados == "Original":  
        data_freq = "Dados Mensais"
    else: 
        data_freq = f"Média {frequencia_dados.title()}"
        eu_ets = eu_ets.groupby(pd.Grouper(freq=agg_freq)).mean()

    fig = px.line(eu_ets, x=eu_ets.index, y="US$", title=f"ETS União Europeia | Preço (US$/tCO2eq)<br><sup>{data_freq}",
                    labels={"index":"","US$":"Preço (EUR/tCO2e)"})

    st.plotly_chart(fig, use_container_width=True)



with california:

    if frequencia_dados in  ["Original","Trimestral"]:  
        data_freq = 'Dados Trimestrais'
    else: 
        data_freq = f"Média {frequencia_dados.title()}"
        california_ets = california_ets.groupby(pd.Grouper(freq=agg_freq)).mean()

    fig = px.line(california_ets, x=california_ets.index, y="US$", title=f"ETS Califórnia e Québec | Preço (US$/tCO2eq)<br><sup>{data_freq}",
                    labels={"index":"","US$":"Preço (EUR/tCO2e)"})

    st.plotly_chart(fig, use_container_width=True)


with china:

    if frequencia_dados == "Original":  
        data_freq = "Dados Mensais"
    else: 
        data_freq = f"Média {frequencia_dados.title()}"
        china_ets = china_ets.groupby([pd.Grouper(freq=agg_freq), "State"]).mean().reset_index("State")

    fig = px.line(china_ets, x=china_ets.index, y="Price", color="State",
                  title=f"ETS Pilotos da China | Preço (US$/tCO2eq) <br><sup>{data_freq}",
                    labels={"index":"","Price":"Preço (EUR/tCO2e)","State":""})
    

    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=0.95, xanchor="right", x=1))
    

    st.plotly_chart(fig, use_container_width=True)

    


with rggi:

    
    if frequencia_dados in  ["Original","Trimestral"]:  
        data_freq = 'Dados Trimestrais'
    else: 
        data_freq = f"Média {frequencia_dados.title()}"
        rggi_ets = rggi_ets.groupby(pd.Grouper(freq=agg_freq)).mean()

    # two axis plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rggi_ets.index, y=rggi_ets["US$"], mode='lines', name='Preço (US$/tCO2eq)'))
    fig.add_trace(go.Scatter(x=rggi_ets.index, y=rggi_ets["VOLUME"], mode='lines', name='Volume (tCO2eq)',yaxis='y2'))

    fig.update_layout(title=f"ETS RGGI (EUA) | Preço (US$/tCO2eq) e Volume de Licenças de Emissão <br><sup>{data_freq}",
                      xaxis_title="",
                      yaxis_title="Preço (US$/tCO2eq)",
                      yaxis2=dict(title="Volume (tCO2eq)", overlaying='y', side='right'),
                      legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1))
    
    st.plotly_chart(fig, use_container_width=True)

