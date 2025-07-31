
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def serie_preco_agg(df, key, st_location=st,groupby="Instrument Type",tipo_mercado='Taxas de Carbono'):

    price_data = df.groupby([groupby,"Year"])["Price"]\
        .agg(["mean","median","min","max"]).dropna(how="all").reset_index()

    agg_dict = {"mean":"Média","median":"Mediana","min":"Mínimo","max":"Máximo"}

    plot_placeholder = st_location.empty()

    aggregation = st_location.radio(
        "Agregar por Preço",
        options=["mean","median","min","max"],
        index=0,
        horizontal=True,
        key=f'{key}_p',
        format_func=lambda x: agg_dict[x]
    )

    if len(price_data[groupby].unique())>1:
        fig = px.line(price_data, x="Year", y=aggregation, color=groupby,
                    labels={groupby:"",aggregation:"","Year":"Ano"})

    else:
        fig = px.line(price_data, x="Year", y=aggregation,
                      labels={groupby:"",aggregation:"US$/tCO2e","Year":"Ano"})

    agg_title = agg_dict[aggregation]
    if agg_title[-1] == 'a':
        agg_title = agg_title[:-1]+"o"
        

    fig.update_layout(

            title=dict(text=f"Evolução do Preço {agg_title} em {tipo_mercado}", font=dict(size=14),),
            showlegend=False,
            width=500,
            height=400,
            
        )

    plot_placeholder.plotly_chart(fig, use_container_width=True)


def serie_emissoes_agg(df, st_location=st,legend=True,groupby="Instrument Type",tipo_mercado='Taxas de Carbono'):

    emissoes = df.groupby([groupby,"Year"])["Emissions"].sum()*100
    emissoes = emissoes.to_frame().reset_index()

    fig = px.line(emissoes, x="Year", y="Emissions", color='Instrument Type',
                    labels={groupby:"","Emissions":"%","Year":"Ano",} )

    fig.update_layout(

            title=dict(text=f"% das Emissões Cobertas por {tipo_mercado}", font=dict(size=14),),
            showlegend=False,
            width=500,
            height=400,

        )
    
    st_location.plotly_chart(fig, use_container_width=True)


def serie_receita_agg(df, key, st_location=st,legend=True,groupby="Instrument Type",tipo_mercado='Taxas de Carbono'):

    receita_data = df.groupby([groupby,"Year"])["Revenue"]\
        .agg(["mean","sum"]).dropna(how="all").reset_index().dropna()

    agg_dict = {"mean":"Média","sum":"Total"}

    plot_placeholder = st_location.empty()

    aggregation = st_location.radio(
        "Agregar por Preço",
        options=["mean","sum"],
        index=0,
        horizontal=True,
        format_func=lambda x: agg_dict[x],
        key=  f"{key}_r",
    )

    
    fig = px.line(receita_data, x="Year", y=aggregation, color='Instrument Type',
                    labels={groupby:"","Year":"Ano",aggregation:"US$ Milhões"}) 

    fig.update_layout(

            title=dict(text=f"Evolução da Receita {agg_dict[aggregation]} em {tipo_mercado}", font=dict(size=14),),
            showlegend=False,
            width=500,
            height=400,
        )

    plot_placeholder.plotly_chart(fig, use_container_width=True)


def compare_series_plot(df, yaxis, legend_name, st_location=st,tipo_mercado='Taxas de Carbono'):

    df = df.dropna(subset=[yaxis]).copy().sort_values(by="Year")

    df["Name of the initiative"]= df["Name of the initiative"]\
                                        .str.replace(" carbon tax","",)\
                                        .str.replace(" Carbon tax","",)

    plot_title = {"Price":f"Evolução do Preço em {tipo_mercado}",
               "Revenue":f"Evolução da Receita em {tipo_mercado}",
               "Emissions":f"% das Emissões Cobertas por {tipo_mercado}"}


    axis_title = {"Price":"US$/tCO2e",
                "Revenue":"Milhões US$",
                "Emissions":"%"}

    if yaxis == "Emissions":
        df[yaxis] = df[yaxis]*100

    fig = px.line(df, x="Year", y=yaxis, color=legend_name,
                    labels={legend_name:"","Year":"Ano",yaxis:axis_title[yaxis]}, )

    fig.update_layout(

            title=dict(text=plot_title[yaxis], font=dict(size=14),),
            
            width=500,
            height=400,

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
    
    st_location.plotly_chart(fig, use_container_width=True)