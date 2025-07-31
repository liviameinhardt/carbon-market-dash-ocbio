#%%
"""
This script reads the data from the World Bank excel file and treats it to be used in the project.
The data is about carbon taxes and includes information about the tax, the price, the revenue and the emissions."""

import pandas as pd 
import numpy as np 
import re

meses = {
    "January": "Janeiro",
    "February": "Fevereiro",
    "March": "Março",
    "April": "Abril",
    "May": "Maio",
    "June": "Junho",
    "July": "Julho",
    "August": "Agosto",
    "September": "Setembro",
    "October": "Outubro",
    "November": "Novembro",
    "December": "Dezembro"
}

def update_wb(file_path='data/raw/dados_wb.xlsx',
              save_path="data/processed",
              countries_info_data="data/raw/extra_country_info.csv"):
    """
    This function reads the data from the World Bank excel file and treats it to be used in the project.

    Args:   
        file_path (str): The path to the excel file.
        save_path (str): The path to save the processed data.
        countries_info_data (str): The path to the csv file with additional country information. (Expected columns: Jurisdiction;Income Group;Region)
    """
    #get update info
    last_update = pd.read_excel(file_path, nrows=1, usecols=[0]).columns[0]\
                        .replace("Data last updated ","")

    mes_traducao = [(k,v) for k,v in meses.items() if k in last_update][0]
    last_update = last_update.replace(mes_traducao[0], mes_traducao[1])

    last_update_db = pd.read_csv('../data/update_info.csv',index_col=0)
    last_update_db.loc['WB'] = last_update

    #read data
    df_info = pd.read_excel(file_path,
                    sheet_name='Compliance_Gen Info',
                    header=1)

    df_info = df_info.replace(" ", np.nan)\
            .dropna(axis=0,how='all')\
            .dropna(axis=1, how='all')
    
    #country name
    df_info["Jurisdiction covered"] = df_info["Jurisdiction covered"].str.strip()

    # Sectors Covered
    # Replace "Yes", "No", and "In principle" with 1, 0, and 0 respectively
    # Create a new column that lists the columns where the value is 1 in that row
    df_info['Sectors Covered'] = df_info[['Electricity and heat',
                        'Industry',
                        'Mining and extractives',
                        'Transport',
                        'Aviation',
                        'Buildings',
                        'Agriculture, forestry and fishing fuel use',
                        'Agricultural emissions',
                        'Waste',
                        'LULUCF']].replace({"Yes": 1, 'No': 0, "In principle": 0})\
                            .apply(lambda row: ', '.join(row.index[row == 1].tolist()), axis=1)


    #split status and dates
    df_info["Start Year"] = df_info["Status"]\
                                .apply(lambda x: int(re.search(r'(\d{4})', x).group(1)) 
                                    if re.search(r'(\d{4})', x) 
                                    else None)

    df_info["End Year"] = df_info["Status"]\
                            .apply(lambda x: int(re.search(r'Abolished.*?(\d{4})', x).group(1)) 
                                if re.search(r'Abolished.*?(\d{4})', x) 
                                else None)
    
    def extract_status(x):
            if "Abolished" in x:
                return "Abolished"
            match = re.search(r'(Implemented|Under consideration|Under development)', x)
            return match.group(1) if match else None

    df_info["Status"] = df_info["Status"].apply(extract_status)

    #get region and income group data from price sheet
    df_price = pd.read_excel(file_path,
                    sheet_name='Compliance_Price',
                    header=1)\
                .replace("-",np.nan)

    #additional info
    info = pd.read_csv(countries_info_data,sep=";",
                    index_col=0)

    #create mapping dicts
    regions_map = df_price.set_index("Jurisdiction Covered")["Region"].to_dict()
    regions_map.update(info['Region'].dropna().to_dict())

    income_g = df_price.set_index("Jurisdiction Covered")["Income group"].to_dict()
    income_g.update(info['Income Group'].dropna().to_dict())

    #apply mapping
    df_info["Region"] = df_info["Jurisdiction covered"].map(regions_map)
    df_info["Income group"] = df_info["Jurisdiction covered"].map(income_g)

    #check for missing data
    print("Missing Region data:",df_info[df_info["Region"].isnull()]["Jurisdiction covered"].values,'\n')
    print("Missing Income Group data:",df_info[df_info["Income group"].isnull()]["Jurisdiction covered"].values,'\n')

    df_info = df_info.drop_duplicates()

    #treat type and subtype
    df_info["Subtype"] = df_info["Type"].str.replace("Carbon tax","").str.replace("ETS","").str.strip()
    df_info["Subtype"] = df_info["Subtype"].str.replace(" or ","/").str.strip()
    df_info["Type"] = df_info["Type"].apply(lambda x: "Carbon tax" if "Carbon tax" in x else "ETS")
    
    #checks for missing data
    missing = df_price[~df_price['Jurisdiction Covered'].isin(df_info["Jurisdiction covered"])]['Jurisdiction Covered']
    print("Price data missing gen. information:",missing.values,'\n')

    #remove NAs
    df_price.dropna(subset=df_price.columns[3:],how="all",inplace=True)

    #DUVDA: COMO SELECIONAR O PRECO PARA OS QUE TEM MAIS DE UM TIPO E NAO SO 'SINGLE PRICE'
    # df_price[df_price["Jurisdiction Covered"].duplicated(keep=False)].to_csv("duplicated_price.csv",decimal=",",sep=";")
    df_price = df_price[~df_price["Name of the initiative"].duplicated(keep=False)]

    #remove columns in df_info
    df_price.drop(["Region","Income group","Metric","Start date","Jurisdiction Covered","Price rate label"],inplace=True, axis=1)
    df_price = df_price.set_index(["Name of the initiative","Instrument Type"])

    #prepare data for time series dataframe
    df_price.columns.name="Year"
    df_price = df_price.stack().to_frame("Price")

    #REVENUE
    df_revenue = pd.read_excel(file_path,
                    sheet_name='Compliance_Revenue',
                    header=1)

    df_revenue = df_revenue.replace("Not available",np.nan)

    df_revenue = df_revenue.drop(['Jurisdiction Covered','Metric',],axis=1)
    df_revenue = df_revenue.set_index(["Name of the initiative",'Instrument Type'])

    df_revenue.columns.name="Year"
    df_revenue = df_revenue.stack().to_frame("Revenue")

    #EMISSIONS
    df_emissions = pd.read_excel(file_path,
                    sheet_name='Compliance_Emissions',
                    header=2)

    df_emissions = df_emissions.dropna(how='all')

    instrument_dict = df_price.reset_index(['Instrument Type','Year'])['Instrument Type'].to_dict()
    instrument_dict.update(df_revenue.reset_index(['Instrument Type','Year'])['Instrument Type'].to_dict())

    df_emissions['Instrument Type'] = df_emissions['Name of the initiative'].map(instrument_dict)

    #fill nan values
    for i, v in df_emissions[df_emissions['Instrument Type'].isnull()].iterrows():
        if "ETS" in v['Name of the initiative']:
            df_emissions.at[i,'Instrument Type'] = "ETS"
        elif "Carbon tax" in v['Name of the initiative']:   
            df_emissions.at[i,'Instrument Type'] = "Carbon tax"
        else:   
            print(v['Name of the initiative'],"is missing instrument type")

    df_emissions = df_emissions.set_index(["Name of the initiative",'Instrument Type'])
    df_emissions = df_emissions.drop("Total")

    df_emissions.columns.name="Year"
    df_emissions = df_emissions.stack().to_frame("Emissions")

    series_wb = pd.concat([df_price,df_revenue,df_emissions],axis=1).reset_index()
    
    #Traducoes 
    df_info["Status"] = df_info["Status"].map({"Implemented":"Implementado",
                                            "Under consideration":"Em consideração",
                                            "Under development":"Em desenvolvimento",
                                            "Abolished":"Extinto"})

    df_info["Subtype"] = df_info["Subtype"].map({"National":"Nacional",
                                                    "Regional":"Regional",
                                                    "Subnational - State/Province":"Subnacional - Estado/Província",
                                                    "Subnational - City":"Subnacional - Município",
                                                    "National Undecided":"Nacional Indeciso"})

    df_info['Type'] = df_info['Type'].map({"Carbon tax":"Taxas de Carbono",
                                            "ETS":"Sistema  de comércio de licenças de emissão (ETS)"})


    series_wb['Instrument Type'] = series_wb['Instrument Type'].map({"Carbon tax":"Taxas de Carbono",
                                                                     "ETS":"ETS"})


    #concat and save time series
    series_wb.to_csv(f"{save_path}/wb_time_series.csv",
                                            index=False,sep=";",decimal=",")

    #save data info
    df_info.to_csv(f"{save_path}/wb_info.csv",
                index=False,sep=";",decimal=",")


    last_update_db.to_csv('data/update_info.csv')

    print("Done WB")


if __name__ == "__main__":
     update_wb()