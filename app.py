import streamlit as st
from streamlit_extras.stateful_button import button
import pdfplumber
import pandas as pd
from datetime import datetime
from io import BytesIO

@st.cache_data
def to_xlsx(dfs):
    output = BytesIO()
    with pd.ExcelWriter(output) as writer:
        for i,df in enumerate(dfs):
            df.to_excel(writer, sheet_name=f"Sheet{i+1}")
    output.seek(0)
    return output


def format(df, template):
    try:
        if template == option1:
            if df.shape[1] != 13:
                raise KeyError(f"Expected 13 columnns, got {df.shape[1]}")
            
            namo, almac, llen = 2, 4, -1

            df.drop(df.shape[0]-1, inplace=True)

            df.iloc[:, almac] = df.iloc[:, almac].astype(float)
            df.iloc[:, namo] = df.iloc[:, namo].astype(float)

            df.iloc[:, llen] = (df.iloc[:, almac] / df.iloc[:, namo] * 100).round(2)

            n = df.shape[0] 
            df.loc[n] = None

            df.iloc[n, almac] = round(df.iloc[:, almac].sum(), 3)
            df.iloc[n, llen] = round(df.iloc[:, llen].mean(), 1)

            output = [df]

        elif template == option2:
            if df.shape[1] != 19:
                raise KeyError(f"Expected 19 columnns, got {df.shape[1]}")
            
            df1 = df.copy().iloc[:,:5]
            df1.dropna(how="all", inplace=True)

            sep = df.iloc[:,12:].isna().all(axis=1).idxmax()
            df2 = pd.concat([df.iloc[:,5:12], df.iloc[:sep,12:]]).copy().dropna(how="all").reset_index(drop=True)

            df3 = df.iloc[sep:,12:].copy().dropna(how="all").reset_index(drop=True).drop([0,1]).reset_index(drop=True)

            output = [df1, df2, df3]

        else:
            output = []

        return output
    except KeyError as e:
        st.error(f"El archivo no sigue el formato esperado para el {template}")
        #st.write(F"Detalles: {e}")
        return []

st.set_page_config(page_title="PDF Converter", layout="wide")
st.title("PDF Converter")

option1 = "Reporte de Presas de Jalisco"
option2 = "Reporte de Hidrometría y Climatología"

template = st.radio("Selecciona el tipo de archivo",
                    options = [option1, option2],
                    index=None)

uploaded_file = st.file_uploader("Selecciona el archivo a convertir",
                                    help = "help is gonna be written here",
                                    type="pdf", accept_multiple_files=False)
file_name = uploaded_file.name[:-4] if uploaded_file else None

click = st.button("Convertir", disabled = (not uploaded_file) and (template is None))

if click and file_name not in st.session_state:
    pdf = pdfplumber.open(uploaded_file)
    table = pdf.pages[0].extract_table()

    df = pd.DataFrame(table[2:], columns=table[0:2])
    index = df.columns
    df.columns = pd.MultiIndex.from_arrays([pd.Series(index.get_level_values(0)).ffill().str.replace("\n", " "),
                                    index.get_level_values(1).str.replace("\n", " ")])
    
    df = df.replace("", None).map(lambda x: x.replace("\n", " ") if isinstance(x, str) else x)

    output_tables = format(df, template)
    if output_tables:
        st.session_state[file_name] = output_tables

if file_name in st.session_state:
    cola, colb, colc = st.columns([0.6,0.2,0.2])
    with cola:
        st.markdown(f":material/table_chart: {file_name}")
    with colc:
        preview = st.toggle(label="Preview", value=False, key=f"preview_{file_name})")
    with colb:
        st.download_button(label="Descargar",
                            data = to_xlsx(st.session_state[file_name]),
                            key = f"download_{file_name})",
                            file_name = f"{file_name}.xlsx",
                            use_container_width=True)

    if preview:
        cols = st.columns(len(st.session_state[file_name]))
        for col, t in zip(cols, st.session_state[file_name]):
            with col:
                st.write(t)
