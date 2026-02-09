import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Simpact Maintenance & Stock", layout="wide")

# --- VOTRE PARC HEIDELBERG ---
LISTE_MACHINES = [
    "Heidelberg CD 102 (Nouvelle)",
    "Heidelberg CD 102",
    "Heidelberg SM 102",
    "Heidelberg SM 74",
    "Heidelberg PM 52",
    "Heidelberg GTO",
    "Massicot (Autre)",
    "Plieuse (Autre)"
]

# --- CONNEXION GOOGLE SHEETS ---
def get_google_sheet():
    try:
        # Récupération du Secret
        if "gcp_service_account" in st.secrets:
            json_key = json.loads(st.secrets["gcp_service_account"]["json_key"])
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
            client = gspread.authorize(creds)
            return client.open("Simpact_Maintenance_DB").sheet1
        else:
            st.error("⚠️ Secret introuvable. Avez-vous configuré les Secrets dans Streamlit ?")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

# --- INTERFACE ---
st.title("🏭 Simpact - Maintenance & Pièces")

# Menu Latéral
menu = st.sidebar.radio("Navigation", ["Nouvelle Intervention", "Historique & Coûts"])

# --- PAGE 1 : SAISIE ---
if menu == "Nouvelle Intervention":
    st.header("📝 Saisie Intervention / Pièce")
    
    with st.form("form_maintenance"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            machine = st.selectbox("Machine", LISTE_MACHINES)
            type_m = st.selectbox("Type", ["Panne (Curative)", "Changement Pièce", "Préventive", "Réglage"])
        
        with col2:
            tech = st.text_input("Technicien")
            heure = st.time_input("Heure", datetime.now())

        st.markdown("---")
        st.markdown("### 🔩 Pièces Détachées (Optionnel)")
        c1, c2 = st.columns(2)
        with c1:
            # Référence Heidelberg
            ref_piece = st.text_input("Référence Pièce (ex: M2.196.1121)", placeholder="Laisser vide si aucune pièce changée")
        with c2:
            prix_piece = st.number_input("Coût de la pièce (DT)", min_value=0.0, step=10.0, format="%.2f")

        desc = st.text_area("Description de l'intervention")
        
        submitted = st.form_submit_button("ENREGISTRER L'INTERVENTION")
        
        if submitted:
            sheet = get_google_sheet()
            if sheet:
                try:
                    # On enregistre tout, y compris le prix et la ref
                    sheet.append_row([
                        str(date), 
                        str(heure), 
                        machine, 
                        type_m, 
                        desc, 
                        ref_piece,  # Nouvelle colonne
                        prix_piece, # Nouvelle colonne
                        tech
                    ])
                    st.success(f"✅ Enregistré ! (Coût pièce : {prix_piece} DT)")
                except Exception as e:
                    st.error(f"Erreur lors de l'écriture : {e}")

# --- PAGE 2 : ANALYSE DES COÛTS ---
elif menu == "Historique & Coûts":
    st.header("💰 Analyse des Coûts de Maintenance")
    
    if st.button("🔄 Actualiser les données"):
        sheet = get_google_sheet()
        if sheet:
            try:
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                
                # Conversion du prix en nombre pour les calculs (sécurité)
                if "Cout_DT" in df.columns:
                    df["Cout_DT"] = pd.to_numeric(df["Cout_DT"], errors='coerce').fillna(0)
                    
                    # 1. KPI GLOBAL
                    total_depense = df["Cout_DT"].sum()
                    st.metric(label="Total Dépenses Pièces (Parc Complet)", value=f"{total_depense:,.2f} DT")
                    
                    st.markdown("---")
                    
                    # 2. TABLEAU PAR MACHINE
                    st.subheader("Détail par Machine")
                    # On groupe par machine et on somme les coûts
                    cout_par_machine = df.groupby("Machine")["Cout_DT"].sum().sort_values(ascending=False)
                    st.bar_chart(cout_par_machine)
                    
                    # 3. TABLEAU DÉTAILLÉ
                    st.subheader("Journal Complet")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Les colonnes 'Cout_DT' ne semblent pas encore exister dans le fichier Excel.")
                    st.dataframe(df)

            except Exception as e:
                st.warning(f"Erreur de lecture ou données vides : {e}")
