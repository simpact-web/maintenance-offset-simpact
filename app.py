import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Simpact Maintenance", layout="wide")

# --- TITRE ET ENTÊTE ---
st.title("🏭 Simpact - Maintenance & Suivi Machines")
st.markdown("---")

# --- LISTE DES MACHINES (À MODIFIER SELON VOTRE PARC) ---
MACHINES = [
    "Heidelberg Speedmaster (SM 74)",
    "KBA Rapida 105",
    "Massicot Polar",
    "Plieuse Horizon",
    "Celle-ci est une machine de test"
]

TYPES_INTERVENTION = [
    "Préventive (Graissage/Nettoyage)",
    "Curative (Panne/Casse)",
    "Amélioration / Réglage",
    "Changement Pièce d'usure"
]

# --- BARRE LATÉRALE (MENU) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2921/2921226.png", width=100)
st.sidebar.header("Menu Technicien")
menu = st.sidebar.radio("Navigation", ["Nouvelle Intervention", "Historique & Journal"])

# --- FONCTION POUR CHARGER LES DONNÉES (TEMPORAIRE) ---
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=["Date", "Heure", "Machine", "Type", "Description", "Technicien"])

# --- PAGE 1 : NOUVELLE INTERVENTION ---
if menu == "Nouvelle Intervention":
    st.subheader("📝 Signaler une maintenance")
    
    with st.form("form_maintenance"):
        col1, col2 = st.columns(2)
        with col1:
            date_op = st.date_input("Date de l'intervention", datetime.now())
            machine = st.selectbox("Machine concernée", MACHINES)
            type_maint = st.selectbox("Type d'intervention", TYPES_INTERVENTION)
        
        with col2:
            tech = st.text_input("Nom du Technicien")
            heure = st.time_input("Heure", datetime.now())
            
        desc = st.text_area("Description détaillée (Panne, Pièces changées, Observations...)")
        
        submit = st.form_submit_button("ENREGISTRER L'INTERVENTION")
        
        if submit:
            new_entry = pd.DataFrame([{
                "Date": date_op,
                "Heure": str(heure),
                "Machine": machine,
                "Type": type_maint,
                "Description": desc,
                "Technicien": tech
            }])
            st.session_state['data'] = pd.concat([st.session_state['data'], new_entry], ignore_index=True)
            st.success("✅ Intervention enregistrée avec succès !")

# --- PAGE 2 : HISTORIQUE ---
elif menu == "Historique & Journal":
    st.subheader("📊 Journal des maintenances")
    df = st.session_state['data']
    
    if df.empty:
        st.info("Aucune intervention enregistrée pour le moment.")
    else:
        st.dataframe(df, use_container_width=True)
        
        # Bouton pour télécharger en Excel (CSV)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger l'historique (CSV)",
            data=csv,
            file_name='maintenance_simpact.csv',
            mime='text/csv',
        )
