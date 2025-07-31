import streamlit as st
import os 

def sobre_dash(st_location=st,expanded=False):
    with st_location.expander("Sobre o Dashboard", expanded=expanded):

        st_location.subheader("O que é o dashboard?")
        st_location.text("O Dashboard de Instrumentos de Precificação Direta de Carbono do FGV Bioeconomia é uma ferramenta interativa desenvolvida para apoiar formuladores de políticas públicas, pesquisadores, investidores e demais stakeholders. O painel reúne e organiza informações sobre mecanismos de precificação direta de carbono, como taxas e mecanismos de mercado (voluntário e regulado), em diferentes países. Este painel combina dados públicos e fontes internacionais reconhecidas, como o World Bank, Ecosystem Marketplace e B3, com análises e insights do FGV Bioeconomia. Seu objetivo é promover transparência, embasar decisões estratégicas e fomentar o debate sobre o papel da precificação de carbono na transição para uma economia de baixo carbono.")

        st_location.subheader("Como está organizado?")
        st_location.markdown("O conteúdo do dashboard está estruturado de forma temática, começando pelos **mecanismos de compliance** de precificação de carbono, que incluem **taxas de carbono** e **mercados regulados**. Em seguida, são apresentados os dados do **mercado voluntário de carbono (MCV)**, com informações sobre créditos emitidos, projetos por escopo e regiões de atuação. Na sequência, uma seção dedicada ao **CBIO (RenovaBio)**. Por fim, o painel apresenta os dados do **CORSIA**, o mecanismo global de compensação de emissões do setor de aviação internacional.")


def pag_config(file_name):

    page_name = file_name[2:].split('.')[0].replace('_', ' ').title()

    st.logo('data/logo.png', icon_image='data/logo.png',size='large')

    st.set_page_config (
        page_title=page_name,
        layout="wide",
        initial_sidebar_state="expanded"
    )