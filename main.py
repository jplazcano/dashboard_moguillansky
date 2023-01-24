import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='JP Analytics', page_icon=None, initial_sidebar_state="auto", menu_items=None)

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




    # La clínica tiene que facturar material de contraste y descartable a veces en la especialidad incorrecta, no es
    # un error, sino que así lo deben hacer. Para el análisis hay que arreglarlo para obtener la cantidad correcta de
    # estudios:

    df.loc[(df["Practica"] == "Material de contraste para tomografía") & (
                df["Especialidad"] == "Tomografia"), "Especialidad"] = "Contrastes"
    df.loc[(df["Practica"] == "Material de Contraste para RMN") & (
                df["Especialidad"] == "Resonancia"), "Especialidad"] = "Contrastes"
    df.loc[(df["Practica"] == "Material descartable para punción prostática") & (
                df["Especialidad"] == "Puncion por Eco"), "Especialidad"] = "Descartables"


    estudios = ['Resonancia', 'Radiologia', 'Angio RM', 'Ecografia',
                'Doppler', 'Mamografia', 'Tomografia', 'Densitometria',
                'Puncion por Eco', 'Angio TAC']

    servicios = ['Resonancia', 'Tomografia', 'Ecografia',
                 'Radiologia', 'Mamografia', 'Densitometria']

    df_sin_insumos = df.loc[df['Especialidad'].isin(estudios)]

    # Facturación y cantidad de estudios e insumos por especialidad

    datos_especialidad_dict = {}
    datos_especialidad_grafico_dict = {}

    for servicio in servicios:
        df_ser = df.loc[df['Servicio'] == servicio]
        monto_por_especialidad = df_ser.groupby('Especialidad')['Cantidad', 'Monto Total'].sum().astype(
            int).sort_values(by='Monto Total', ascending=False)

        total_monto = monto_por_especialidad['Monto Total'].sum()
        total_cantidad = monto_por_especialidad['Cantidad'].sum()

        fig1 = go.Figure(data=[go.Bar(x=monto_por_especialidad.index,
                                      y=monto_por_especialidad['Monto Total'])])
        fig1.update_layout(
            xaxis=dict(title="Especialidad", showgrid=True, gridcolor='lightgray', gridwidth=1),
            yaxis=dict(title="Monto ($)", showgrid=True, gridcolor='lightgray', gridwidth=1),
            title="Monto Por Especialidad",
        )

        fig2 = go.Figure(data=[go.Bar(x=monto_por_especialidad.index,
                                      y=monto_por_especialidad['Cantidad'])])
        fig2.update_layout(
            xaxis=dict(title="Especialidad", showgrid=True, gridcolor='lightgray', gridwidth=1),
            yaxis=dict(title="Monto ($)", showgrid=True, gridcolor='lightgray', gridwidth=1),
            title="Cantidad Por Especialidad",
        )

        monto_por_especialidad.loc['Total'] = [total_cantidad, total_monto]

        monto_por_especialidad = monto_por_especialidad.assign(
            Porcentaje=lambda x: x['Monto Total'] / total_monto * 100).round(2)

        monto_por_especialidad = monto_por_especialidad.assign(
            Media=lambda x: x['Monto Total'] / x['Cantidad'])

        monto_por_especialidad['Media'] = monto_por_especialidad['Media'].astype(int)

        # monto_por_especialidad = monto_por_especialidad.style.format(
        # {'Monto Total': "$ {:,.0f}", 'Porcentaje': "{:,.2f} %", 'Cantidad': '{:,.0f}'})
        datos_especialidad_dict[servicio] = monto_por_especialidad
        datos_especialidad_grafico_dict[servicio] = fig1, fig2

    # Facturación y cantidad de estudios e insumos por equipo

    datos_por_equipo_dict = {}
    for servicio in servicios:
        df_ser = df_sin_insumos.loc[df_sin_insumos['Servicio'] == servicio]
        monto_por_equipo = df_ser.groupby('Equipo')['Cantidad', 'Monto Total'].sum().astype(int).sort_values(
            by='Monto Total', ascending=False)
        total_monto = monto_por_equipo['Monto Total'].sum()
        total_cantidad = monto_por_equipo['Cantidad'].sum()
        monto_por_equipo.loc['Total'] = [total_cantidad, total_monto]
        monto_por_equipo = monto_por_equipo.assign(Porcentaje=lambda x: x['Monto Total'] / total_monto * 100)


        # monto_por_equipo = monto_por_equipo.style.format(
        # {'Monto Total': "$ {:,.0f}", 'Porcentaje': "{:,.2f} %", 'Cantidad': '{:,.0f}'})
        datos_por_equipo_dict[servicio] = monto_por_equipo

    # Facturación y cantidad de estudios e insumos por obra social

    datos_por_os_dict = {}
    for servicio in servicios:
        df_ser_sin_insumos = df_sin_insumos.loc[df_sin_insumos['Servicio'] == servicio]
        df_ser_con_insumos = df.loc[df['Servicio'] == servicio]

        cantidad_por_os = df_ser_sin_insumos.groupby('Obra Social')['Cantidad'].sum().astype(int).sort_values(
            ascending=False).to_frame()
        monto_por_os = df_ser_con_insumos.groupby('Obra Social')['Monto Total'].sum().astype(int).sort_values(
            ascending=False).to_frame()

        new_df = cantidad_por_os.merge(monto_por_os, on='Obra Social')

        total_monto = new_df['Monto Total'].sum()
        total_cantidad = new_df['Cantidad'].sum()
        new_df.loc['Total'] = [total_cantidad, total_monto]

        new_df = new_df.assign(Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad * 100)
        new_df = new_df.assign(Porcentaje_monto=lambda x: x['Monto Total'] / total_monto * 100)
        new_df = new_df.assign(Media=lambda x: x['Monto Total'] / x['Cantidad'])
        new_df['Media'] = new_df['Media'].astype(int)

        #  new_df = new_df.style.format(
        #      {'Monto Total': "$ {:,.0f}", 'Porcentaje_cantidad': "{:,.2f} %", 'Cantidad': '{:,.0f}',
        #      'Porcentaje_monto': "{:,.2f} %"})
        datos_por_os_dict[servicio] = new_df

    # Facturación y cantidad de estudios e insumos por práctica

    datos_por_practica_dict = {}
    for servicio in servicios:
        df_ser = df.loc[df['Servicio'] == servicio]

        datos_por_practica = df_ser.groupby('Practica')['Cantidad', 'Monto Total'].sum().astype(int).sort_values(
            by='Monto Total', ascending=False)

        total_monto = datos_por_practica['Monto Total'].sum()
        total_cantidad = datos_por_practica['Cantidad'].sum()
        datos_por_practica.loc['Total'] = [total_cantidad, total_monto]

        datos_por_practica = datos_por_practica.assign(
            Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad * 100)
        datos_por_practica = datos_por_practica.assign(
            Porcentaje_monto=lambda x: x['Monto Total'] / total_monto * 100)
        datos_por_practica = datos_por_practica.assign(
            Media=lambda x: x['Monto Total'] / x['Cantidad'])
        datos_por_practica = datos_por_practica.fillna(0)
        datos_por_practica['Media'] = datos_por_practica['Media'].astype(int)

        # datos_por_practica = datos_por_practica.style.format(
        # {'Monto Total': "$ {:,.0f}", 'Porcentaje_cantidad': "{:,.2f} %", 'Cantidad': '{:,.0f}',
        #  'Porcentaje_monto': "{:,.2f} %"})
        datos_por_practica_dict[servicio] = datos_por_practica

    # Facturación y cantidad de estudios e insumos por médico derivante

    datos_por_md_dict = {}
    for servicio in servicios:
        df_por_md = df_sin_insumos.loc[df_sin_insumos['Servicio'] == servicio]

        datos_por_md = df_por_md.groupby('Medico Derivante')['Cantidad', 'Monto Total'].sum().astype(int).sort_values(
            by='Monto Total', ascending=False)

        total_monto = datos_por_md['Monto Total'].sum()
        total_cantidad = datos_por_md['Cantidad'].sum()
        datos_por_md.loc['Total'] = [total_cantidad, total_monto]

        datos_por_md = datos_por_md.assign(Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad * 100)
        datos_por_md = datos_por_md.assign(Porcentaje_monto=lambda x: x['Monto Total'] / total_monto * 100)
        datos_por_md = datos_por_md.assign(Media=lambda x: x['Monto Total'] / x['Cantidad'])
        datos_por_md['Media'] = datos_por_md['Media'].astype(int)

        #datos_por_md = datos_por_md.style.format(
         #   {'Monto Total': "$ {:,.0f}", 'Porcentaje_cantidad': "{:,.2f} %", 'Cantidad': '{:,.0f}',
           #  'Porcentaje_monto': "{:,.2f} %",
             #'Media_estudio': "$ {:,.0f}"})
        datos_por_md_dict[servicio] = datos_por_md

    selected_service = st.selectbox("Select a service:", servicios)
    st.header('Servicio de ' + selected_service)
    st.subheader('Servicio de ' + selected_service + ' por Especialidad')
    st.dataframe(datos_especialidad_dict[selected_service], use_container_width=True)
    st.plotly_chart(datos_especialidad_grafico_dict[selected_service][1])
    st.plotly_chart(datos_especialidad_grafico_dict[selected_service][0])
    st.subheader('Servicio de ' + selected_service + ' por Equipo')
    st.dataframe(datos_por_equipo_dict[selected_service], use_container_width=True)
    st.subheader('Servicio de ' + selected_service + ' por Obra Social')
    st.dataframe(datos_por_os_dict[selected_service], use_container_width=True)
    st.subheader('Servicio de ' + selected_service + ' por Práctica')
    st.dataframe(datos_por_practica_dict[selected_service], use_container_width=True)
    st.subheader('Servicio de ' + selected_service + ' por Médico Derivante')
    st.dataframe(datos_por_md_dict[selected_service], use_container_width=True)

