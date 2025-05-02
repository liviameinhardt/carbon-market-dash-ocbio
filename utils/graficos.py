
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def serie_preco_agg(df, key, st_location=st,legend=True,groupby="Instrument Type"):

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
                    labels={groupby:""})
        
    else:
        fig = px.line(price_data, x="Year", y=aggregation)


    fig.update_layout(

            title=dict(text=f"Evolução do Preço por Tipo de Iniciativa | {agg_dict[aggregation]}", font=dict(size=14),),
            
            width=500,
            height=500,

            showlegend=legend,
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


def serie_emissoes_agg(df, st_location=st,legend=True,groupby="Instrument Type"):

    emissoes = df.groupby([groupby,"Year"])["Emissions"].sum()*100
    emissoes = emissoes.to_frame().reset_index()

    fig = px.line(emissoes, x="Year", y="Emissions", color='Instrument Type',
                    labels={groupby:""}, )

    fig.update_layout(

            title=dict(text=f"% das Emissões Cobertas por Tipo de Iniciativa", font=dict(size=14),),
            
            width=500,
            height=500,

            showlegend=legend,
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


def serie_receita_agg(df, key, st_location=st,legend=True,groupby="Instrument Type"):

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
                    labels={groupby:""}, 
                    )

    fig.update_layout(

            title=dict(text=f"Evolução da Receita {agg_dict[aggregation]} por Tipo de Iniciativa", font=dict(size=14),),
            
            width=500,
            height=500,

            showlegend=legend,
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


def compare_series_plot(df, yaxis, legend_name, st_location=st):

    df = df.dropna(subset=[yaxis]).copy().sort_values(by="Year")

    df["Name of the initiative"]= df["Name of the initiative"]\
                                        .str.replace(" carbon tax","",)\
                                        .str.replace(" Carbon tax","",)


    fig = px.line(df, x="Year", y=yaxis, color=legend_name,
                    labels={legend_name:""}, )

    fig.update_layout(

            title=dict(text=yaxis, font=dict(size=14),),
            
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
    
    st_location.plotly_chart(fig, use_container_width=True)