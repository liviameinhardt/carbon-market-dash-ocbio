#%%
import pandas as pd 
from datetime import datetime
import numpy as np 


def update_mvc(file_path='data/raw/dados_mvc.xlsx'):
        
    df = pd.read_excel(file_path,
                    sheet_name='PROJECTS',
                    header=3)

    current_year = datetime.now().year

    #correct column names
    df.columns = df.columns.astype(str).str.strip().str.replace('\n', '', regex=False)
    df = df.set_index("Project ID")
    df = df.replace({"":np.nan," ":np.nan}).dropna(axis=0,how='all')

    #filter columns
    cols_keep = ['Project Name',
                'Voluntary Registry',
                'Voluntary Status',
                'Scope',
                'Type',
                'Reduction / Removal',
                'Region',
                'Country',
                'Project Developer',
                'Total Credits Issued',
                'Total Credits Retired',
                'Total Credits Remaining',
                'First Year of Project (Vintage)',]

    #years columns to keep 
    retired_credits = df[[f"{i}.1" for i in range(1996,current_year)]] #por retirada
    issued_credtis = df[[f"{i}.3" for i in range(1996,current_year)]] #por emissão
    vintage_credits = df[[str(i) for i in range(1996,current_year)]] #por vencimento

    df = df[cols_keep]	

    #traduzir
    traducao_setores = {
                "Agriculture": "Agricultura",
                "Carbon Capture & Storage": "Captura e Armazenamento de Carbono",
                "Chemical Processes": "Processos Químicos",
                "Forestry & Land Use": "Florestas e Uso da Terra",
                "Household & Community": "Domicílios e Comunidades",
                "Industrial & Commercial": "Industrial e Comercial",
                "Renewable Energy": "Energia Renovável",
                "Transportation": "Transporte",
                "Waste Management": "Gestão de Resíduos"
            }

    df["Scope"] = df["Scope"].map(traducao_setores)
        
    regioes_traduzidas = {
        "North America": "América do Norte",
        "Latin America and the Caribbean": "América Latina e Caribe",
        "Western Asia": "Ásia Ocidental",
        "Europe": "Europa",
        "South-Eastern Asia": "Sudeste Asiático",
        "Sub-Saharan Africa": "África Subsaariana",
        "Oceania": "Oceania",
        "Southern Asia": "Ásia Meridional",
        "Eastern Asia": "Ásia Oriental",
        "Northern Africa": "África Setentrional",
        "Eastern Europe": "Europa Oriental",
        "Central Asia": "Ásia Central",
        "International": "Internacional"
    }

    df['Region'] = df['Region'].map(regioes_traduzidas)

    #split time series data
    retired_credits.columns = retired_credits.columns.str.replace(".1","").astype(int)
    issued_credtis.columns = issued_credtis.columns.str.replace(".3","").astype(int)
    vintage_credits.columns = vintage_credits.columns.astype(int)

    vintage_credits.columns.name="Ano"
    retired_credits.columns.name="Ano"
    issued_credtis.columns.name="Ano"

    retired_credits = retired_credits.stack().to_frame("Aposentados")
    issued_credtis = issued_credtis.stack().to_frame("Emitidos (data de emissão)")
    vintage_credits = vintage_credits.stack().to_frame("Emitidos (data de redução/remoção)")

    credits = pd.concat([retired_credits,issued_credtis,vintage_credits],axis=1).replace(0,np.nan).dropna()
   
    #save data
    credits.to_csv("data/processed/mvc_credits.csv",sep=";",decimal=",")
    df.to_csv("data/processed/mvc_credits_info.csv",sep=";",decimal=",")

    print("Done MCV")
    

if __name__ == "__main__":
    update_mvc()
# %%
