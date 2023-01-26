import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from matplotlib.pyplot import *

st.set_page_config(page_title='JP Analytics', page_icon=None, initial_sidebar_state="auto", menu_items=None)


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
    df['Dia'] = df['Fecha Turno'].dt.weekday

    min_date = df['Fecha Turno'].min().strftime('%d/%m/%Y')
    max_date = df['Fecha Turno'].max().strftime('%d/%m/%Y')


    df = df.fillna(0)

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

    cant_rm = df_sin_insumos[df_sin_insumos['Especialidad'].isin(['Resonancia', 'Angio RM'])].sum()

    # Facturación y cantidad de estudios e insumos por especialidad

    datos_especialidad_dict = {}
    datos_especialidad_grafico_dict = {}
    for servicio in servicios:
        df_ser = df.loc[df['Servicio'] == servicio]
        monto_por_especialidad = df_ser.groupby('Especialidad')['Cantidad', 'Monto Total'].sum().astype(
            int).sort_values(by='Monto Total', ascending=False)

        total_monto = monto_por_especialidad['Monto Total'].sum()
        total_cantidad = monto_por_especialidad['Cantidad'].sum()

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(x=monto_por_especialidad.index,
                             y=monto_por_especialidad['Cantidad'],
                             name='Cantidad',
                             marker_color='#176ba0',
                             opacity=1,
                             width=0.3,
                             offset=-0.3),
                      secondary_y=False)

        fig.add_trace(go.Bar(x=monto_por_especialidad.index,
                             y=monto_por_especialidad['Monto Total'],
                             name='Monto ($)',
                             marker_color='#1de4bd',
                             opacity=1,
                             width=0.3,
                             offset=0),
                      secondary_y=True)

        fig.update_layout(title='Cantidad y monto facturado por Especialidad -  Servicio de ' + str(servicio))

        monto_por_especialidad.loc['Total'] = [total_cantidad, total_monto]

        monto_por_especialidad = monto_por_especialidad.assign(
            Porcentaje=lambda x: x['Monto Total'] / total_monto * 100).round(2)

        monto_por_especialidad = monto_por_especialidad.assign(
            Media=lambda x: x['Monto Total'] / x['Cantidad'])
        monto_por_especialidad = monto_por_especialidad.fillna(0)
        monto_por_especialidad['Media'] = monto_por_especialidad['Media'].astype(int)

        datos_especialidad_dict[servicio] = monto_por_especialidad
        datos_especialidad_grafico_dict[servicio] = fig

    # Facturación y cantidad de estudios e insumos por equipo
    datos_por_equipo_dict = {}
    datos_por_equipo_grafico_dict = {}
    for servicio in servicios:

        df_ser_sin_insumos1 = df_sin_insumos.loc[df_sin_insumos['Servicio'] == servicio]
        df_ser_con_insumos1 = df.loc[df['Servicio'] == servicio]

        cantidad_por_equipo = df_ser_sin_insumos1.groupby('Equipo')['Cantidad'].sum().astype(int).sort_values(
            ascending=False).to_frame()
        monto_por_equipo = df_ser_con_insumos1.groupby('Equipo')['Monto Total'].sum().astype(int).sort_values(
            ascending=False).to_frame()

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(x=monto_por_equipo.index,
                             y=cantidad_por_equipo['Cantidad'],
                             name='Cantidad',
                             marker_color='#176ba0',
                             opacity=1,
                             width=0.3,
                             offset=-0.3),
                      secondary_y=False)

        fig.add_trace(go.Bar(x=monto_por_equipo.index,
                             y=monto_por_equipo['Monto Total'],
                             name='Monto ($)',
                             marker_color='#1de4bd',
                             opacity=1,
                             width=0.3,
                             offset=0),
                      secondary_y=True)

        fig.update_layout(title='Cantidad y monto facturado por Equipo -  Servicio de ' + str(servicio))

        new_df1 = cantidad_por_equipo.merge(monto_por_equipo, on='Equipo')

        total_monto1 = new_df1['Monto Total'].sum()
        total_cantidad1 = new_df1['Cantidad'].sum()
        new_df1.loc['Total'] = [total_cantidad1, total_monto1]
        new_df1 = new_df1.fillna(0)
        new_df1 = new_df1.assign(Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad1 * 100)
        new_df1 = new_df1.assign(Porcentaje_monto=lambda x: x['Monto Total'] / total_monto1 * 100)
        new_df1 = new_df1.assign(Ratio=lambda x: x['Porcentaje_monto'] / x['Porcentaje_cantidad'])
        new_df1 = new_df1.assign(Media_estudio=lambda x: x['Monto Total'] / x['Cantidad'])
        new_df1['Media_estudio'] = new_df1['Media_estudio'].astype(int)


        datos_por_equipo_dict[servicio] = new_df1
        datos_por_equipo_grafico_dict[servicio] = fig


    # Facturación y cantidad de estudios e insumos por obra social

    datos_por_os_dict = {}
    datos_por_os_grafico_dict = {}
    for servicio in servicios:
        df_ser_sin_insumos = df_sin_insumos.loc[df_sin_insumos['Servicio'] == servicio]
        df_ser_con_insumos = df.loc[df['Servicio'] == servicio]

        cantidad_por_os = df_ser_sin_insumos.groupby('Obra Social')['Cantidad'].sum().astype(int).sort_values(
            ascending=False).to_frame()
        monto_por_os = df_ser_con_insumos.groupby('Obra Social')['Monto Total'].sum().astype(int).sort_values(
            ascending=False).to_frame()

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(x=monto_por_os.iloc[:15].index,
                             y=cantidad_por_os['Cantidad'],
                             name='Cantidad',
                             marker_color='#176ba0',
                             opacity=1,
                             width=0.3,
                             offset=-0.3),
                      secondary_y=False)

        fig.add_trace(go.Bar(x=monto_por_os.iloc[:15].index,
                             y=monto_por_os['Monto Total'],
                             name='Monto ($)',
                             marker_color='#1de4bd',
                             opacity=1,
                             width=0.3,
                             offset=0),
                      secondary_y=True)

        fig.update_layout(title='Cantidad y monto facturado por Obra Social -  Servicio de ' + str(servicio) + ' (top 15)')

        new_df = cantidad_por_os.merge(monto_por_os, on='Obra Social')

        total_monto = new_df['Monto Total'].sum()
        total_cantidad = new_df['Cantidad'].sum()
        new_df.loc['Total'] = [total_cantidad, total_monto]
        new_df = new_df.fillna(0)
        new_df = new_df.assign(Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad * 100)
        new_df = new_df.assign(Porcentaje_monto=lambda x: x['Monto Total'] / total_monto * 100)
        new_df = new_df.assign(Ratio=lambda x: x['Porcentaje_monto'] / x['Porcentaje_cantidad'])
        new_df = new_df.assign(Media_estudio=lambda x: x['Monto Total'] / x['Cantidad'])
        new_df['Media_estudio'] = new_df['Media_estudio'].astype(int)

        datos_por_os_dict[servicio] = new_df
        datos_por_os_grafico_dict[servicio] = fig

    # Facturación y cantidad de estudios e insumos por práctica

    datos_por_practica_dict = {}
    datos_por_practica_figura_dict = {}
    for servicio in servicios:
        df_ser = df.loc[df['Servicio'] == servicio]

        datos_por_practica = df_ser.groupby('Practica')['Cantidad', 'Monto Total'].sum().astype(int).sort_values(
            by='Monto Total', ascending=False)

        total_monto = datos_por_practica['Monto Total'].sum()
        total_cantidad = datos_por_practica['Cantidad'].sum()
        datos_por_practica.loc['Total'] = [total_cantidad, total_monto]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(x=monto_por_os.iloc[:15].index,
                             y=cantidad_por_os['Cantidad'],
                             name='Cantidad',
                             marker_color='#176ba0',
                             opacity=1,
                             width=0.3,
                             offset=-0.3),
                      secondary_y=False)

        fig.add_trace(go.Bar(x=monto_por_os.iloc[:15].index,
                             y=monto_por_os['Monto Total'],
                             name='Monto ($)',
                             marker_color='#1de4bd',
                             opacity=1,
                             width=0.3,
                             offset=0),
                      secondary_y=True)

        fig.update_layout(
            title='Cantidad y monto facturado por Obra Social -  Servicio de ' + str(servicio) + ' (top 15)')
        datos_por_practica = datos_por_practica.fillna(0)
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
        datos_por_practica_figura_dict[servicio] = fig

    # Facturación y cantidad de estudios e insumos por médico derivante

    datos_por_md_dict = {}
    datos_por_md_grafico_dict = {}
    for servicio in servicios:
        df_por_md = df_sin_insumos.loc[df_sin_insumos['Servicio'] == servicio]

        datos_por_md = df_por_md.groupby('Medico Derivante')['Cantidad', 'Monto Total'].sum().astype(int).sort_values(
            by='Monto Total', ascending=False)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(x=datos_por_md.iloc[:25].index,
                             y=datos_por_md['Cantidad'],
                             name='Cantidad',
                             marker_color='#176ba0',
                             opacity=1,
                             width=0.3,
                             offset=-0.3),
                      secondary_y=False)

        fig.add_trace(go.Bar(x=datos_por_md.iloc[:25].index,
                             y=datos_por_md['Monto Total'],
                             name='Monto ($)',
                             marker_color='#1de4bd',
                             opacity=1,
                             width=0.3,
                             offset=0),
                      secondary_y=True)

        fig.update_layout(title='Cantidad de estudios y monto facturado por Médico Derivante Servicio de ' + str(servicio) + ' (top 25)')

        total_monto = datos_por_md['Monto Total'].sum()
        total_cantidad = datos_por_md['Cantidad'].sum()
        #datos_por_md.loc['Total'] = [total_cantidad, total_monto]


        datos_por_md = datos_por_md.fillna(0)
        datos_por_md = datos_por_md.assign(Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad * 100)
        datos_por_md = datos_por_md.assign(Porcentaje_monto=lambda x: x['Monto Total'] / total_monto * 100)
        datos_por_md = datos_por_md.assign(Media_estudio=lambda x: x['Monto Total'] / x['Cantidad'])
        datos_por_md = datos_por_md.assign(Ratio=lambda x: x['Porcentaje_monto'] / x['Porcentaje_cantidad'])
        datos_por_md['Media_estudio'] = datos_por_md['Media_estudio'].astype(int)


        datos_por_md_dict[servicio] = datos_por_md
        datos_por_md_grafico_dict[servicio] = fig

    st.sidebar.title("Menú")
    selection = st.sidebar.selectbox(" ",["Resúmen General", "Datos por Servicio", "Section 3"])
    if selection == 'Datos por Servicio':

        selected_service = st.selectbox("Elegí un servicio:", servicios)

        st.header('Servicio de ' + selected_service)
        st.write(
            f'Durante el período evaluado, comprendido entre el {min_date} y el {max_date}, la clínica llevó a cabo'
              f' un total de '
        )
        st.subheader('Servicio de ' + selected_service + ' por Especialidad')
        st.dataframe(datos_especialidad_dict[selected_service].style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                      use_container_width=True)

        if st.button('Exportar a Excel', key=10):
            datos_especialidad_dict[selected_service].to_excel(f'datos_por_especialidad_{selected_service}.xlsx')

        show_graph = st.checkbox('Mostrar gráfico', value=True, key=1)
        if show_graph:
            st.plotly_chart(datos_especialidad_grafico_dict[selected_service])

        st.subheader('Servicio de ' + selected_service + ' por Equipo')
        st.dataframe(datos_por_equipo_dict[selected_service].style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)

        if st.button('Exportar a Excel', key=20):
            datos_por_equipo_dict[selected_service].to_excel(f'datos_por_equipo_{selected_service}.xlsx')

        show_graph = st.checkbox('Mostrar gráfico', value=True, key=2)
        if show_graph:
            st.plotly_chart(datos_por_equipo_grafico_dict[selected_service])

        st.subheader('Servicio de ' + selected_service + ' por Obra Social')
        st.dataframe(datos_por_os_dict[selected_service].style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)
        if st.button('Exportar a Excel', key=30):
            datos_por_os_dict[selected_service].to_excel(f'datos_por_os{selected_service}.xlsx')

        show_graph = st.checkbox('Mostrar gráfico', value=True, key=3)
        if show_graph:
            st.plotly_chart(datos_por_os_grafico_dict[selected_service])


        st.subheader('Servicio de ' + selected_service + ' por Práctica')
        st.dataframe(datos_por_practica_dict[selected_service].style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)
        if st.button('Exportar a Excel', key=40):
            datos_por_practica_dict[selected_service].to_excel(f'datos_por_practica_{selected_service}.xlsx')

        show_graph = st.checkbox('Mostrar gráfico', value=True, key=4)


        if show_graph:
            st.plotly_chart(datos_por_practica_figura_dict[selected_service])

        st.subheader('Servicio de ' + selected_service + ' por Médico Derivante')
        min_quantity = st.slider('Selecciona la mínima canidad de estudios enviados:',
                                 min_value=int(datos_por_md_dict[selected_service]['Cantidad'].min()),
                                 max_value=int(datos_por_md_dict[selected_service]['Cantidad'].max()),
                                 value=10,
                                 step=1)

        st.dataframe(datos_por_md_dict[selected_service][datos_por_md_dict[selected_service]['Cantidad'] >= min_quantity].style.format({'Monto Total': "$ {:,.0f}",
                                                                                                                                        'Porcentaje_cantidad': "{:,.2f} %",
                                                                                                                                        'Cantidad': '{:,.0f}',
                                                                                                                                        'Porcentaje_monto': "{:,.2f} %",
                                                                                                                                        'Porcentaje': "{:,.2f} %",
                                                                                                                                        'Media_estudio': "$ {:,.0f}",
                                                                                                                                     'Cantidad':'{:,.0f}'}),use_container_width=True)
        show_graph = st.checkbox('Mostrar gráfico', value=True, key=5)

        if st.button('Exportar a Excel', key=50):
            datos_por_md_dict[selected_service].to_excel(f'datos_por_md_{selected_service}.xlsx')

        if show_graph:
            st.plotly_chart(datos_por_md_grafico_dict[selected_service])


