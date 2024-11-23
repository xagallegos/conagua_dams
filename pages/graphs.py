import os
import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def graficas_monitoreo(clavesih, param="ALMACENAMIENTO", nam="NAMO", **kwargs):
    filtered_data = st.session_state.all_local_data[st.session_state.all_local_data["clavesih"] == clavesih]
    nam_name = nam.lower()
    nam_name += "almac" if param == "ALMACENAMIENTO" else "elev"
    param_name = "almacenaactual" if param == "ALMACENAMIENTO" else "elevacionactual"
    porcentaje = filtered_data[param_name] / filtered_data[nam_name] * 100

    return go.Scatter(x=filtered_data["fechamonitoreo"], y=porcentaje, **kwargs)


if "conagua_data" not in st.session_state:
    st.session_state.conagua_data = {}
    path = "./data/sih"

    for file_name in os.listdir(path):
        full_path = os.path.join(path, file_name)
        clavesih = file_name.split(".")[0]

        df = pd.read_csv(full_path,
                         skiprows = 7, 
                         parse_dates = ["Fecha"],
                         date_format = "%Y/%m/%d")
        
        df["Fecha"] = df["Fecha"].dt.date
        df.columns = [col.strip() for col in df.columns]
        df.replace({"-":None}, inplace=True)
        st.session_state.conagua_data[clavesih] = df
        st.session_state.data_updates["sih"] = df["Fecha"].max()


st.title("Visualizaciones")

keys = st.session_state.all_local_data["clavesih"].unique()

# sinav / sih info
sinav_date = st.session_state.data_updates["sinav"].strftime("%d/%m/%Y")
sih_date = st.session_state.data_updates["sih"].strftime("%d/%m/%Y")

sinav_url = "https://sinav30.conagua.gob.mx:8080/Presas/"
sih_url = "https://sih.conagua.gob.mx/"


with st.expander("Almacenamiento (hm³)"):
    traces = [graficas_monitoreo(key, "ALMACENAMIENTO", "NAMO", name=key) for key in keys]
    fig = go.Figure(data=traces)
    fig.update_layout(
        yaxis_title="Almacenamiento (%)",
        xaxis_title="Fecha")
    st.plotly_chart(fig)

    st.markdown(f"**Fecha de extracción**: {sinav_date}")
    st.markdown(f"**Fuente:** [Sistema Nacional de Información del Agua, CONAGUA.]({sinav_url})")

with st.expander("Llenado (msnm)"):
    traces = [graficas_monitoreo(key, "LLENADO", "NAMO", name=key) for key in keys]
    fig = go.Figure(data=traces)
    fig.update_layout(
        yaxis_title="Llenado (%)",
        xaxis_title="Fecha")
    st.plotly_chart(fig)

    st.markdown(f"**Fecha de extracción**: {sinav_date}")
    st.markdown(f"**Fuente:** [Sistema Nacional de Información del Agua, CONAGUA.]({sinav_url})")

with st.expander("Evaporación"):
    traces = [go.Scatter(x=df["Fecha"], y=df["Evaporación(mm)"], name=key) for key, df in st.session_state.conagua_data.items()]
    fig = go.Figure(data=traces)
    fig.update_layout(
        yaxis_title="Evaporación (mm)",
        xaxis_title="Fecha")
    st.plotly_chart(fig)

    st.markdown(f"**Fecha de extracción**: {sih_date}")
    st.markdown(f"**Fuente:** [Sistema de Información Hidrológica, CONAGUA.]({sih_url})")

with st.expander("Almacenamiento promedio por mes"):
    traces = []
    for key in keys:
        df = st.session_state.all_local_data[st.session_state.all_local_data["clavesih"] == key]
        df["porcentaje"] = df["almacenaactual"] / df["namoalmac"] * 100
        df["fechamonitoreo"] = pd.to_datetime(df["fechamonitoreo"])
        grouped = df.groupby(df["fechamonitoreo"].dt.month)["porcentaje"].mean()
        traces.append(go.Scatter(x=grouped.index, y=grouped, name=key))
    fig = go.Figure(data=traces)
    fig.update_layout(
        yaxis_title="Almacenamiento (%)",
        xaxis_title="Mes")
    st.plotly_chart(fig)

    st.markdown(f"**Fecha de extracción**: {sinav_date}")
    st.markdown(f"**Fuente:** [Sistema Nacional de Información del Agua, CONAGUA.]({sinav_url})")

# Por área?
