import streamlit as st


st.logo('data/logo.png', icon_image='data/logo.png',size='large')
st.set_page_config (
    page_title="Sobre",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(""" 
### 📊 **Dashboard: Precificação de Carbono**  

O **Observatório de Conhecimento e Inovação em Bioeconomia (OCBio)** da **FGV Agro** apresenta o **Dashboard de Precificação de Carbono**, uma ferramenta interativa que traz um panorama global sobre os dois principais mecanismos de precificação direta do carbono:  

✅ **Taxa de carbono**  
✅ **Mercado de carbono**  

A precificação do carbono é essencial para reduzir as emissões de gases de efeito estufa (GEE), incentivando investimentos mais sustentáveis e mudanças nos padrões de produção e consumo.  

**O que você encontra no dashboard?**  
✔️ Dados atualizados de mais de **10 fontes confiáveis**  
✔️ Análises visuais e interativas sobre políticas de precificação de carbono  
✔️ Explicações sobre os diferentes mercados e seus funcionamentos

""")

st.link_button("Saiba mais sobre a FGV Agro",
               url="https://agro.fgv.br/")

# st.markdown("##")
# st.subheader("Fontes de Dados")