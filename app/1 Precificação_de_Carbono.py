import streamlit as st  
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config (
    page_title="Precificação de Carbono",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar os dados
data_wb = pd.read_csv("data\processed\wb_info.csv",sep=";",decimal=",")
series_wb = pd.read_csv("data\processed\wb_time_series.csv",sep=";",decimal=",")


# Informações gerais
st.title("Precificação de Carbono")
st.text("Fonte: Banco Mundial (Abril, 2024)") #automatico (criar um info.txt)
st.markdown("##")

# Estatisticas de data_wb
percent_emissoes = sum(data_wb["Share of global emissions covered"].dropna())*100
percent_emissoes_ano_anterior = sum(data_wb[data_wb["Start Year"]<data_wb["Start Year"].max()]["Share of global emissions covered"].dropna())*100
crescimento_percent_emissoes = percent_emissoes - percent_emissoes_ano_anterior

implementadas = data_wb[data_wb['Status']=="Implemented"]
iniciativas_implementadas = len(implementadas["Instrument name"].unique())
iniciativas_anteriores = len(implementadas[implementadas["Start Year"]<implementadas["Start Year"].max()]["Instrument name"].unique())
crescimento_iniciativas = iniciativas_implementadas - iniciativas_anteriores

preco_medio = series_wb[series_wb["Year"]==series_wb["Year"].max()]["Price"].dropna().mean()
preco_medio_ano_anterior = series_wb[series_wb["Year"]==series_wb["Year"].max()-1]["Price"].dropna().mean()
crescimento_preco_medio = preco_medio - preco_medio_ano_anterior

#como deixar claro que o deltaé em relação ao ano anterior?
metrics_col = st.columns(3)
metrics_col[0].metric(f"Iniciativas Implementadas", iniciativas_implementadas, f"{crescimento_iniciativas}", border=True)
metrics_col[1].metric("Percentual de emissões globais cobertas", f"{percent_emissoes:.2f}%",delta=f"{crescimento_percent_emissoes:.2f}%", border=True)
metrics_col[2].metric("Preço médio (US$/tCO2e)", f"{preco_medio:.2f}", delta=f"{crescimento_preco_medio:.2f} USD", border=True)

st.markdown("##")

#Mapa das Iniciativas
mapa, filtros = st.columns([3,1])

with filtros:

    st.subheader("Filtros")

    status = st.selectbox(
        "Status",
        options=data_wb["Status"].unique()
    )

    tipo = st.multiselect(
        "Subtype",
        options=data_wb["Subtype"].unique(),
        default=data_wb["Subtype"].unique()
    )

    if status=="Implemented":
            
        tamanho_marcador = st.radio(
            "Tamanho do marcador",
            options=["% de cobertura da jurisdição", "Padrão"],
            index=0
        ) 
    else:

        tamanho_marcador =  "Padrão"

with mapa:

    map_data = data_wb[(data_wb["Status"]==status) &
                        (data_wb["Subtype"].isin(tipo)) &
                        (data_wb["lat"].notnull() )]
    
    map_data["Share of jurisdiction emissions covered"].fillna(0,inplace=True)
    hover_txt = {col:False for col in map_data.columns}

    if status  == "Implemented":
        hover_txt["Share of jurisdiction emissions covered"] =  f":.2%"
        hover_txt["Share of global emissions covered"] = f":.2%"
        hover_txt["Subtype"] = True
    else:
        hover_txt["Subtype"] = True

    # mapa = st.radio("Mapa", ("Open Street Map", "Natural Earth"), index=0, horizontal=True)

    # if mapa == "Open Street Map":
    #     fig = px.scatter_map(map_data, lat="lat", lon="lon", color="Type",
    #                     hover_name="Instrument name", hover_data=hover_txt,
    #                     size= None if tamanho_marcador=="Padrão" else "Share of jurisdiction emissions covered",
    #                     labels={"Type":"Tipo de Iniciativa"},
    #                     map_style='open-street-map', zoom=0.7)
        
        # fig.update_traces(cluster=dict(enabled=True))

# else:
    fig = px.scatter_geo(map_data, lat="lat", lon="lon", color="Type",
                    hover_name="Instrument name", hover_data=hover_txt,
                    size= None if tamanho_marcador=="Padrão" else "Share of jurisdiction emissions covered",
                        projection="equirectangular",
                    labels={"Type":"Tipo de Iniciativa"})
    
    fig.update_geos(fitbounds="locations", visible=False, showcountries=True)
    
    substitle = "" if tamanho_marcador=="Padrão" else "Marcadores proporcionais ao percentual de cobertura da jurisdição"
    title = f'Iniciativas de precificação de carbono | {status} <br><sup>{substitle}'

    fig.update_layout(
    
        title=dict(text=title, font=dict(size=20),),
            
            width=700,
            height=700,

            showlegend=True,
            legend=dict(
                orientation="v",x=0,xanchor="center",
                y=1,yanchor="auto", font=dict(size=15)
            ),
        )


    st.plotly_chart(fig, use_container_width=True)


#Gráfico de barras/linhas tipos de Iniciativas 
st.markdown("##")
st.header("Distribuição de Iniciativas")

barras, linhas = st.columns(2)

with barras:

    col1, col2 = st.columns(2)

    eixo_x = col1.radio(
        "Agregar por",
        options=["Region", "Income group"],horizontal=True,index=1
    )

    filtro_dados = col2.radio(
        "Tipo da Iniciativa",
        options=data_wb["Type"].unique(),
        horizontal=True)
    
    barra_data = data_wb[data_wb["Type"]==filtro_dados].groupby([eixo_x,'Status'])["Subtype"]\
                        .count()\
                        .to_frame().reset_index()

    fig = px.bar(barra_data, x=eixo_x, 
                 y="Subtype", color="Status", 
                 barmode='group',
                text_auto=True,
                 labels={"Subtype":"Número de Iniciativas","Status":""},
                 title=f"Distribuição de Iniciativas {filtro_dados} por {eixo_x} e Status",)



    fig.update_layout(

            width=800,
            height=700,

            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
        )
    

    
    st.plotly_chart(fig, use_container_width=True)


with linhas:

    filtro_dados = st.radio(
        "Status da Iniciativa",
        options=data_wb["Status"].unique(),
        horizontal=True
    )

    linhas_data = data_wb[(data_wb["Status"]==filtro_dados)].groupby(["Start Year","Type"])["Instrument name"]\
            .count().to_frame().reset_index()
    
    linhas_data = linhas_data\
        .join(linhas_data.groupby("Type")["Instrument name"].cumsum().to_frame("Total"))

    fig = px.line(linhas_data, x="Start Year",
                   y="Total", color='Type',
                   labels={"Type":""},
                   title=f"Distribuição de Iniciativas por Ano e Tipo | {filtro_dados}",
                   )
    
    fig.update_layout(

            width=800,
            height=700,

            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
        )
    

    st.plotly_chart(fig, use_container_width=True)
    

st.markdown("##")
st.header("Evolução no tempo")

preco, emissoes, receita = st.columns(3)

with preco:

    price_data = series_wb.groupby(["Instrument Type","Year"])["Price"]\
        .agg(["mean","median","min","max"]).dropna(how="all").reset_index()

    agg_dict = {"mean":"Média","median":"Mediana","min":"Mínimo","max":"Máximo"}

    plot_placeholder = st.empty()

    aggregation = st.radio(
        "Agregar por Preço",
        options=["mean","median","min","max"],
        index=0,
        horizontal=True,

        format_func=lambda x: agg_dict[x]
    )

    
    fig = px.line(price_data, x="Year", y=aggregation, color='Instrument Type',
                    labels={"Instrument Type":""}, 
                    )

    fig.update_layout(

            title=dict(text=f"Evolução do Preço por Tipo de Iniciativa | {agg_dict[aggregation]}", font=dict(size=20),),
            
            width=500,
            height=500,

            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
        )

    plot_placeholder.plotly_chart(fig, use_container_width=True)


with emissoes:
    
    emissoes = series_wb.groupby(["Instrument Type","Year"])["Emissions"].sum()*100
    emissoes = emissoes.to_frame().reset_index()

    fig = px.line(emissoes, x="Year", y="Emissions", color='Instrument Type',
                    labels={"Instrument Type":""}, )

    fig.update_layout(

            title=dict(text=f"% das Emissões Cobertas por Tipo de Iniciativa", font=dict(size=20),),
            
            width=500,
            height=500,

            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
        )
    
    st.plotly_chart(fig, use_container_width=True)


with receita:



    receita_data = series_wb.groupby(["Instrument Type","Year"])["Revenue"]\
        .agg(["mean","sum"]).dropna(how="all").reset_index().dropna()

    agg_dict = {"mean":"Média","sum":"Total"}

    plot_placeholder = st.empty()

    aggregation = st.radio(
        "Agregar por Preço",
        options=["mean","sum"],
        index=0,
        horizontal=True,
        format_func=lambda x: agg_dict[x]
    )

    
    fig = px.line(receita_data, x="Year", y=aggregation, color='Instrument Type',
                    labels={"Instrument Type":""}, 
                    )

    fig.update_layout(

            title=dict(text=f"Evolução da Receita {agg_dict[aggregation]} por Tipo de Iniciativa", font=dict(size=20),),
            
            width=500,
            height=500,

            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
        )

    plot_placeholder.plotly_chart(fig, use_container_width=True)

