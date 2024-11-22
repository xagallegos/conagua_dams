import os
import datetime
import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data
def load_local_data(years) -> pd.DataFrame:
    '''
    Loads all local data (if existent) for requested year(s)

    Parameters:
        - years (int | list[int]): year(s) to retrieve
    
    Returns:
        - data (pd.DataFrame): containing saved data from year(s),
                               empty pd.DataFrame if data not existent
    '''
    if isinstance(years, int):
        years = [years]

    data = []
    for y in years:
        file_path = f"./data/monitoreo/data_{y}.csv"
        if os.path.exists(file_path):
            data.append(pd.read_csv(file_path, parse_dates=["fechamonitoreo"], date_format="%Y-%m-%d"))
    if data:
        df = pd.concat(data)
        df["fechamonitoreo"] = df["fechamonitoreo"].dt.date
        return df
    else:
        return pd.DataFrame()


st.set_page_config(page_title="Monitoreo de Presas - Jalisco")


if "all_local_data" not in st.session_state:
    current_year = datetime.today().year
    st.session_state.all_local_data = load_local_data(range(1995,current_year+1))


pg = st.navigation([
    st.Page("graphs_page.py", title="Visualizaciones"),
    st.Page("scraping_page.py", title="Datos de monitoreo"),
    st.Page("pdf_converter_page.py", title="Convertidor PDF")
])

pg.run()
