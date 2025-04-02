import streamlit as st  
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config (
    page_title="Créditos de Carbono",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Créditos de Carbono")
st.write("Fontes: Berkeley carbon trading project (2025); Ecosystem Marketplace (2022)")
st.markdown("##")

st.header("Mercado de Créditos de Carbono")

mvc_credits = pd.read_csv("..\data\processed\mvc_credits.csv", sep=";", decimal=",",index_col=0)
mvc_credits_info = pd.read_csv("..\data\processed\mvc_credits_info.csv", sep=";", decimal=",",index_col=0)

mvc_credits_info.rename(columns={"First Year of Project (Vintage)":"Start Year"},inplace=True)


#copia para parte 2 do dash
credits_pais = mvc_credits.copy()
pais_info = mvc_credits_info.copy()

iso_countries = pd.read_csv("..\data\processed\iso_countries.csv", sep=";", decimal=",",index_col=1)

## filtros ## 
col1, col2 = st.columns([1, 5])

dado = col1.radio("Mapa",("Total Créditos Emitidos","Número de Projetos"))

anos_disp = mvc_credits_info["Start Year"].dropna().astype(int).sort_values().unique()[::-1]
tempo = col1.selectbox("Ano Início",["Total"]+list(anos_disp),
                             help="Total será a soma de todos os anos disponíveis.")


setor = col1.selectbox("Setor",["Todos"]+list(mvc_credits_info["Scope"].sort_values().unique()),
                                help="Todos será a soma de todos os setores disponíveis")

## prepara dados ##
if tempo != "Total":
    mvc_credits_info = mvc_credits_info[mvc_credits_info["Start Year"] == tempo]
    tempo_info = tempo

else:
    tempo_info = f"{mvc_credits_info["Start Year"].min()} - {mvc_credits_info["Start Year"].max()}"

if setor != "Todos":
    mvc_credits_info= mvc_credits_info[mvc_credits_info["Scope"] == setor]
    setor_info = setor
else:
    setor_info = f"<sup>{', '.join(mvc_credits_info["Scope"].unique())}</sup>"

#apply filter to timeseries data
mvc_credits = mvc_credits[mvc_credits.index.isin(mvc_credits_info.index)]


if not len(mvc_credits_info):
    col2.warning("Nenhum projeto corresponde aos filtros selecionados.")

else:
    creditos_pais = mvc_credits_info.groupby("Country")["Total Credits Issued"].agg(["count","sum"])\
        .rename(columns={"count":"Número de Projetos","sum":"Total Créditos Emitidos"})

    creditos_pais  = creditos_pais[creditos_pais.index.isin(iso_countries.index)] #exclude international projects 
    creditos_pais = creditos_pais.join(iso_countries)

    ## gráficos ## 

    fig = px.choropleth(creditos_pais,
                        locations="ISO",
                        color=creditos_pais[dado],
                        hover_name=creditos_pais.index,
                        hover_data=["Total Créditos Emitidos","Número de Projetos"],
                        labels={"Total Créditos Emitidos":"Total Créditos Emitidos",
                                "Número de Projetos":"Número de Projetos"},
                        scope="world")

    fig.update_geos(fitbounds="locations", visible=False, showcountries=True)

    fig.update_layout(

        title=dict(text=f"{dado} por País | {tempo_info} <br>{setor_info}", font=dict(size=20),),
            height=500,

            showlegend=True,
            legend=dict(
                orientation="v",x=0,xanchor="center",
                y=1,yanchor="auto", font=dict(size=15)
            ),

        )

    col2.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)

cut_at = setor_info.find(",",80)
setor_info= "<sup>Todos os setores disponíveis" if setor == "Todos" else f"<sup>{setor_info}"

#creditos por tempo
summary_credits = mvc_credits.groupby("Year").sum()
summary_credits.rename(columns={"Retired Credits":"Aposentados",
                                "Issued Credits":"Emitidos",
                                "Vintage Credits":"Vencidos"}, inplace=True)

fig  = px.line(summary_credits,
            title=f"Créditos Emitidos e Aposentados | {tempo_info}<br>{setor_info}",
            labels={"value":"Total de Créditos", "Year":"Ano","variable":""},)

fig.update_layout(legend=dict(orientation="h", yanchor="bottom",x=0.05, y=1,font=dict(size=12)))

col1.plotly_chart(fig, use_container_width=True)

# por tipo
summary_objective = mvc_credits_info.groupby("Reduction / Removal")["Total Credits Issued"].count().sort_values().to_frame("total")
summary_objective["percent"] = summary_objective.div(summary_objective.sum())*100
summary_objective["percent"] = summary_objective["percent"].round(2).astype(str) + "%"

fig  = px.bar(summary_objective,x="total",text="percent",
              title=f"Créditos por Tipo de Projeto | {tempo_info}<br>{setor_info}",
            labels={"total":"Número de Projetos", "Reduction / Removal":"Objetivo"})
col2.plotly_chart(fig, use_container_width=True)

# por escopo
summary_objective = mvc_credits_info.groupby("Voluntary Registry")["Total Credits Issued"].count().sort_values().to_frame("total")
summary_objective["percent"] = summary_objective.div(summary_objective.sum())*100
summary_objective["percent"] = summary_objective["percent"].round(2).astype(str) + "%"

fig  = px.bar(summary_objective,x="total",text="percent",
              title=f"Créditos por Registro Voluntário | {tempo_info}<br>{setor_info}",
            labels={"total":"Número de Projetos", "Voluntary Registry":"Registro Voluntário"})
col3.plotly_chart(fig, use_container_width=True)

st.subheader("Créditos de Carbono por Localização")


col1, col2, col3, col4 = st.columns(4)

LOCAIS_DICT = {"Region":"Região", "Country":"País"}
visualizar_por = col1.radio("Visualizar por:", ("Region", "Country"),horizontal=True,format_func=lambda x:LOCAIS_DICT[x])
visualizar = col2.radio("Visualizar",("Número de Projetos","Total Créditos Emitidos"))

anos_possiveis = list(pais_info["Start Year"].dropna().astype(int).sort_values().unique()[::-1])
tempo = col3.selectbox("Ano Início",["Total"]+anos_possiveis,help="Total será a soma de todos os anos disponíveis.",key=2)

CATEGORIAS_DICT = {"Reduction / Removal":"Tipo de Projeto","Voluntary Registry":"Registro","Scope":"Setor","Total":"Total" }
separar_por = col4.selectbox("Separar por:", ("Total","Scope", "Voluntary Registry","Reduction / Removal"),help="Total será a soma de projetos disponíveis",key=3,
                             format_func=lambda x: CATEGORIAS_DICT[x])


escolher_top = False #inicializar variavel 

if tempo != "Total":
    pais_info = pais_info[pais_info["Start Year"]== tempo]
    tempo_info = f"em {tempo}"

else:
    tempo_info = f"entre {min(anos_possiveis)} à {max(anos_possiveis)}"

    if visualizar_por == "Country":
        escolher_top = col1.toggle("Filtrar Número de Países", True)


if separar_por != "Total":
    data_plot = pais_info.groupby([visualizar_por,separar_por])["Total Credits Issued"].agg(["count","sum"])\
                .rename(columns={"count":"Número de Projetos","sum":"Total Créditos Emitidos"})

    data_plot = data_plot[visualizar].unstack(level=1)

else:
    data_plot = pais_info.groupby(visualizar_por)["Total Credits Issued"].agg(["count","sum"])\
        .rename(columns={"count":"Número de Projetos","sum":"Total Créditos Emitidos"})[[visualizar]]
    
    
data_plot['total'] = data_plot.sum(axis=1)

if escolher_top:
    
    cola, colb = col1.columns(2)
    top_num = cola.number_input("Número de Países", min_value=1, max_value=len(pais_info["Country"].unique()), value=10, step=1)
    maiores = colb.checkbox("Maiores", True)

    data_plot=data_plot.sort_values(by="total", ascending=not maiores).replace(0,np.nan).dropna(how='all')[:top_num]

    
    subtitle = f"<sup> Top {top_num} Países com {'Maior' if maiores else 'Menor'} {visualizar}"

else:
    subtitle = ""

# else:
data_plot=data_plot.sort_values(by="total", ascending=True).drop("total", axis=1)


fig = px.bar(data_plot,
             y=data_plot.index,
             x=data_plot.columns,
            title=f"{visualizar} por {visualizar_por} | Projetos Iniciados {tempo_info} <br>{subtitle}",
            labels={separar_por:CATEGORIAS_DICT[separar_por],visualizar_por:LOCAIS_DICT[visualizar_por],"value":visualizar}
             )

st.plotly_chart(fig, use_container_width=True)


##################### 
st.header("Mercado Voluntário de Créditos de Carbono")

col1, col2 = st.columns(2)

ver_dados_por = col1.radio("Ver dados por:", ("Região", "Setor"),horizontal=True)

df_regiao  = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="Data_Benchmarking _Region",index_col=[0,1])
df_setor  = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="Data_Benchmarking _Sector",index_col=[0,1])

df_selecionado = df_regiao if ver_dados_por == "Região" else df_setor

volume = col2.radio("Comparar Volume",("Total","Porcentagem"),horizontal=True) #como deixar mais claro?

#graficos mercado 
col1, col2 = st.columns(2)

#volume de créditos 
df_selecionado = df_selecionado.unstack(level=1)

if volume == "Porcentagem":
    df_selecionado["VOLUME"] = df_selecionado["VOLUME"].div(df_selecionado["VOLUME"].fillna(0).sum(axis=1), axis=0)

info_vol = "%" if volume == "Porcentagem" else "Total"

fig = px.bar(df_selecionado["VOLUME"].fillna(0),
            title=f"Volume de Créditos de Carbono por {ver_dados_por}",
            labels={"value": f"Volume {info_vol}", "ANO": ""})

if volume == "Porcentagem":
    fig.update_layout(yaxis_tickformat = '.00%',)

col2.plotly_chart(fig, use_container_width=True)

fig = px.bar(df_selecionado["PREÇO"].fillna(0),
            barmode="group",
            title=f"Preço dos Créditos de Carbono por {ver_dados_por}",
            labels={"value": f"Preço $", "ANO": ""})

fig.update_layout(yaxis_tickformat = '$,',)

col1.plotly_chart(fig, use_container_width=True)

