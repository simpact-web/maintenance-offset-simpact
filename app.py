import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Simpact Maintenance", layout="wide")

# --- VOTRE LISTE DE MACHINES ---
LISTE_MACHINES = [
    "Heidelberg CD 102 (Nouvelle)",
    "Heidelberg CD 102",
    "Heidelberg SM 102",
    "Heidelberg SM 74",
    "Heidelberg PM 52",
    "Heidelberg GTO",
    "Massicot (Autre)", # J'ai laissé ça au cas où
    "Plieuse (Autre)"
]

# --- CONNEXION GOOGLE SHEETS (Le Cerveau) ---
def get_google_sheet():
    # C'est ici que l'application va chercher le mot de passe dans les "Secrets"
    try:
        json_key = json.loads(st.secrets["gcp_service_account"]["json_key"])
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
        client = gspread.authorize(creds)
        return client.open("Simpact_Maintenance_DB").sheet1
    except Exception as e:
        st.error("⚠️ Erreur de connexion aux Secrets. Avez-vous bien collé le JSON dans les réglages Streamlit ?")
        return None

# --- INTERFACE ---
st.title("🏭 Simpact - Suivi Maintenance")

# Menu
menu = st.sidebar.radio("Menu", ["Nouvelle Intervention", "Historique"])

if menu == "Nouvelle Intervention":
    st.header("📝 Saisie Intervention")
    
    with st.form("form_maintenance"):
        # Ligne 1
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            # C'est ici que votre liste s'affiche
            machine = st.selectbox("Machine", LISTE_MACHINES)
        with col2:
            tech = st.text_input("Technicien / Opérateur")
            heure = st.time_input("Heure", datetime.now())

        # Ligne 2
        type_m = st.selectbox("Type d'intervention", ["Préventive (Graissage)", "Curative (Panne)", "Réglage/Calage", "Pièce d'usure"])
        desc = st.text_area("Description détaillée (Problème, pièce changée...)")
        
        submitted = st.form_submit_button("ENREGISTRER")
        
        if submitted:
            sheet = get_google_sheet()
            if sheet:
                try:
                    # On envoie les données vers Google Sheets
                    sheet.append_row([str(date), str(heure), machine, type_m, desc, tech])
                    st.success(f"✅ Intervention enregistrée pour la {machine} !")
                except Exception as e:
                    st.error(f"Erreur lors de l'écriture : {e}")

elif menu == "Historique":
    st.header("📊 Historique des Pannes")
    if st.button("🔄 Actualiser"):
        sheet = get_google_sheet()
        if sheet:
            try:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.info("Aucune donnée pour l'instant ou erreur de lecture.")
