import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='JP Analytics', page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

image = Image.open('/Users/juanpe/Desktop/dashboard_moguillansky/Screenshot 2023-01-23 at 20.14.19.png')
st.image(image)

# TITULO / INSTRUCCIONES
archivo = st.sidebar.file_uploader("", type="xls", accept_multiple_files=True)
if archivo is not None:
    dfs = []
    if len(archivo) > 1:
        for f in archivo:
            df = pd.read_excel(f)
            dfs.append(df)
        df = pd.concat(dfs)
    elif len(archivo) == 1:
        df = pd.read_excel(archivo[0])
    else:
        df = None

    # SECCIÓN 1: Análisis General
if df is not None:

    # Agrego número de día, mes y año
    df['Año'] = df['Fecha Turno'].dt.year
    df['Mes'] = df['Fecha Turno'].dt.month
    df['Día'] = df['Fecha Turno'].dt.weekday
    df_sin_insumos = df[df['Especialidad'].isin(['Ecografia', 'Resonancia', 'Radiologia', 'Angio RM',
                                                 'Mamografia', 'Doppler', 'Tomografia', 'Densitometria',
                                                 'Puncion por Eco', 'Angio TAC', 'Puncion por TAC'])]

    # La clínica tiene que facturar material de contraste y descartable a veces en la especialidad incorrecta, no es
    # un error, sino que así lo deben hacer. Para el análisis hay que arreglarlo para obtener la cantidad correcta de
    # estudios:

    df.loc[(df["Practica"] == "Material de contraste para tomografía") & (
                df["Especialidad"] == "Tomografia"), "Especialidad"] = "Contrastes"
    df.loc[(df["Practica"] == "Material de Contraste para RMN") & (
                df["Especialidad"] == "Resonancia"), "Especialidad"] = "Contrastes"
    df.loc[(df["Practica"] == "Material descartable para punción prostática") & (
                df["Especialidad"] == "Puncion por Eco"), "Especialidad"] = "Descartables"
