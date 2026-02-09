import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Simpact Maintenance", layout="wide")

# --- CONNEXION GOOGLE SHEETS ---
def get_google_sheet():
    # On récupère le secret qu'on a collé dans Streamlit
    json_key = json.loads(st.secrets["gcp_service_account"]["json_key"])
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
    client = gspread.authorize(creds)
    # Ouvre la feuille (Attention au nom exact !)
    return client.open("Simpact_Maintenance_DB").sheet1

# --- INTERFACE ---
st.title("🏭 Simpact - Suivi Maintenance")

# Menu
menu = st.sidebar.radio("Menu", ["Nouvelle Intervention", "Historique"])

if menu == "Nouvelle Intervention":
    st.header("📝 Saisie")
    with st.form("form"):
        date = st.date_input("Date", datetime.now())
        machine = st.selectbox("Machine", ["Heidelberg SM 74", "KBA Rapida 105", "Massicot", "Plieuse"])
        type_m = st.selectbox("Type", ["Préventive", "Curative (Panne)", "Réglage"])
        desc = st.text_area("Description")
        tech = st.text_input("Technicien")
        
        submitted = st.form_submit_button("ENREGISTRER")
        
        if submitted:
            try:
                sheet = get_google_sheet()
                # On ajoute la ligne dans le Google Sheet
                sheet.append_row([str(date), datetime.now().strftime("%H:%M"), machine, type_m, desc, tech])
                st.success("✅ Sauvegardé dans Google Sheets !")
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")

elif menu == "Historique":
    st.header("📊 Données en direct")
    if st.button("🔄 Actualiser les données"):
        try:
            sheet = get_google_sheet()
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.warning("Aucune donnée ou erreur de connexion.")
