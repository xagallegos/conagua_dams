import streamlit as st
import requests
import datetime
from datetime import datetime, timedelta
from io import BytesIO
from stqdm import stqdm
import pandas as pd


@st.cache_data
def fetch_and_filter_data(start_date: datetime, end_date: datetime, keys: list[str]) -> list:
    """
    Fetches data from the API from start_date to end_date, filters it by 'clavesih',
    and saves each day's filtered data into a JSON file.

    Parameters:
    - start_date (datetime): The starting date as a datetime object (inclusive).
    - end_date (datetime): The ending date as a datetime object (inclusive).
    - output_dir (str): Directory where JSON files will be saved.

    Returns:
    - historic_data (list)
    """
    delta = timedelta(days=1)

    current_date = start_date
    historic_data = []

    date_range = (end_date - current_date).days + 1
    pb = stqdm(total=date_range, desc="Progress")
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        url = f"https://sinav30.conagua.gob.mx:8080/PresasPG/presas/reporte/{date_str}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Filter the data by 'clavesih'
            filtered_data = [entry for entry in data if entry.get('clavesih') in keys]

            if filtered_data:
                # Save the filtered data to a JSON file
                historic_data.extend(filtered_data)
                #print(f"\tSuccesfully fetched data for {date_str}")
            else:
                pass
                #print(f"No matching data for {date_str}. Data not fetched.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {date_str}: {e}")
        except ValueError:
            print(f"Invalid JSON received for {date_str}")
        except IOError as e:
            print(f"Error saving data for {date_str}: {e}")

        current_date += delta
        pb.update(1)

    return historic_data


def get_data(date_range: list[datetime, datetime], keys: list[str] | None = None):
    local_data = st.session_state.all_local_data

    if not local_data.empty:
        local_data = local_data[local_data["clavesih"].isin(keys)] if keys else local_data
        lower, upper = local_data["fechamonitoreo"].min(), local_data["fechamonitoreo"].max()
        local_data = local_data[(local_data["fechamonitoreo"] >= date_range[0]) & (local_data["fechamonitoreo"] <= date_range[1])]

        missing_data = []

        if date_range[0] < lower:
            missing_data = missing_data + fetch_and_filter_data(date_range[0], lower - timedelta(days=1), keys)

        if date_range[1] > upper:
            missing_data = missing_data + fetch_and_filter_data(upper + timedelta(days=1), date_range[1], keys)
        
        missing_df = pd.DataFrame(missing_data)
        all_data = pd.concat([local_data, missing_df])

    else:
        all_data = pd.DataFrame(fetch_and_filter_data(date_range[0], date_range[1], keys))

    return all_data


def save_json(data: pd.DataFrame):
    buffer = BytesIO()
    data.to_json(buffer, force_ascii=True)
    #buffer.write(json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8'))
    buffer.seek(0)
    return buffer


def save_csv(data: pd.DataFrame):
    buffer = BytesIO()
    data.to_csv(buffer, index=None, encoding="utf-8")
    buffer.seek(0)
    return buffer


st.title("Data Scraping")
date_range = st.date_input("Rango de fechas",
                            value = (datetime.now() - timedelta(days=31), datetime.now()),
                            format = "DD/MM/YYYY")

col1, col2 = st.columns(2)

with col1:
    selected_keys = st.multiselect("Claves", options=["ESLJL", "EGCJL", "REDJL"])
with col2:
    file_format = st.radio("Formato", options=["CSV", "JSON"], horizontal=True)


if st.button("Extraer Datos:"):
    if len(date_range) != 2:
        st.error("Selecciona un rango de fechas")
    elif not selected_keys:
        st.warning("Selecciona claves para filtrar")
    else:
        # Fetch data
        data = get_data(date_range, selected_keys)

        # Save data according to the selected file format
        if file_format == "CSV":
            file = save_csv(data)
        else:
            file = save_json(data)
            
        # Provide a download link for the saved file
        filename = "data.csv" if file_format == "CSV" else "data.json"
        st.download_button(label="Descargar",
                            data=file,
                            file_name=filename)