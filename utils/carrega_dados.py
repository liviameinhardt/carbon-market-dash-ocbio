import pandas as pd 

def get_ets_data():

    eu_ets  = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="EU_ETS_Carbon_permits")
    california_ets  = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="CaliforniaQuébec_Carbon")
    china_ets = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="CHINA_ETS")
    rggi_ets = pd.read_excel("data/processed/DADOS_MANUAIS.xlsx", sheet_name="RGGI_USD_Volume")

    eu_ets["Date"] = pd.to_datetime(eu_ets["Date"])
    california_ets["Date"] = pd.to_datetime(california_ets["Date"])
    china_ets["Date"] = pd.to_datetime(china_ets["Date"])
    rggi_ets["Date"] = pd.to_datetime(rggi_ets["Date"])

    return eu_ets, california_ets, china_ets, rggi_ets