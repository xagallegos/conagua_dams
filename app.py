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
        file_path = f"./data/sinav/data_{y}.csv"
        if os.path.exists(file_path):
            data.append(pd.read_csv(file_path, parse_dates=["fechamonitoreo"], date_format="%Y-%m-%d"))

    if data:
        df = pd.concat(data)
        df["fechamonitoreo"] = df["fechamonitoreo"].dt.date
        return df
    else:
        return pd.DataFrame()

def home_page():
    st.title("Agua, ¿cómo vamos? III")
    st.subheader("Proyecto de Aplicación Profesional - PAP4J10A")


    st.text("Esta herramienta está desarrollada para proporcionar al Seminario Permanente del Agua \
            acceso a datos estadísticos y geoespaciales clave, así como herramientas avanzadas para \
            su procesamiento y visualización. Su objetivo es ofrecer a los investigadores insumos \
            oficiales y propios que faciliten el desarrollo de investigaciones innovadoras y de alto \
            impacto social. Con este apoyo, se busca evaluar la eficiencia de las políticas de gestión \
            del agua y diseñar estrategias efectivas para la adaptación al cambio climático.")
    

st.set_page_config(page_title="Monitoreo de Presas - Jalisco")
st.logo("https://oci02.img.iteso.mx/Identidades-De-Instancia/ITESO/Logos%20ITESO/Logo-ITESO-Vertical-SinFondo.png")


if "all_local_data" not in st.session_state:
    current_year = datetime.today().year
    st.session_state.all_local_data = load_local_data(range(1995,current_year+1))


# pls update timestamps when updating data
if "data_updates" not in st.session_state:
    st.session_state.data_updates = {"sinav": st.session_state.all_local_data["fechamonitoreo"].max()}


pg = st.navigation([
    st.Page(home_page, title="Inicio", icon=":material/home:"),
    st.Page("./pages/graphs.py", title="Visualizaciones", icon=":material/stacked_bar_chart:"),
    st.Page("./pages/scraping.py", title="Datos de monitoreo", icon=":material/download:"),
    st.Page("./pages/pdf_converter.py", title="Convertidor PDF", icon=":material/picture_as_pdf:")
])

pg.run()
