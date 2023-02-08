import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
from matplotlib.pyplot import *

st.set_page_config(page_title='Dashboard MEDXXI', page_icon=None, initial_sidebar_state="auto", menu_items=None)


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

    #RESUMEN GENERAL

    total_facturacion = int(df['Monto Total'].sum())
    #facturacion por centro
    fac_por_centro = df.groupby(['Centro'])['Monto Total'].sum().astype(int).sort_values(
        ascending=False)

    fac_por_centro = fac_por_centro.to_frame().assign(
        Porcentaje=lambda x: x['Monto Total'] / total_facturacion * 100).round(2)


    grafico_fac_por_centro = make_subplots(rows=1, cols=1)
    grafico_fac_por_centro.add_trace(
        go.Bar(x=fac_por_centro.index,
               y=fac_por_centro['Monto Total'],
               marker=dict(color='#16c2d5'),
               text = fac_por_centro['Monto Total'].apply(lambda x: "<b>${:,.0f}<b>".format(x)),
               textposition='auto'))


    grafico_fac_por_centro.update_layout(
        title='Facturación por Centro',
        xaxis_title='Centro',
        yaxis_title='Monto Total'
    )

    grafico_fac_por_centro_pie = go.Figure(data=[go.Pie(labels=fac_por_centro.index, values=fac_por_centro['Porcentaje'],
                                title='Facturación por Centro', marker=dict(colors=['#16c2d5', '#10217d', '#527c88', '#d7baad', '#6d4dd3', '#f46f74', '#9c94dc']))])

    total_porcentaje = 100
    fac_por_centro.loc['Total'] = [total_facturacion, total_porcentaje]

    #facturacion por servicio
    fac_por_servicio = df.groupby(['Servicio'])['Monto Total'].sum().astype(int).sort_values(
        ascending=False)

    fac_por_servicio = fac_por_servicio.to_frame().assign(
        Porcentaje=lambda x: x['Monto Total'] / total_facturacion * 100).round(2)

    grafico_fac_por_servicio = make_subplots(rows=1, cols=1)
    grafico_fac_por_servicio.add_trace(
        go.Bar(x=fac_por_servicio.index,
               y=fac_por_servicio['Monto Total'],
               marker=dict(color='#16c2d5'),
               text = fac_por_servicio['Monto Total'].apply(lambda x: "<b>${:,.0f}<b>".format(x)),
               textposition='auto'))


    grafico_fac_por_servicio.update_layout(
        title='Facturación por Servicio',
        xaxis_title='Centro',
        yaxis_title='Monto Total'
    )

    grafico_fac_por_servicio_pie = go.Figure(
        data=[go.Pie(labels=fac_por_servicio.index, values=fac_por_servicio['Porcentaje'],
                     title='Facturación por Servicio',
                     marker=dict(colors=['#16c2d5', '#10217d', '#527c88', '#d7baad', '#6d4dd3', '#f46f74', '#9c94dc']))])

    fac_por_servicio.loc['Total'] = [total_facturacion, total_porcentaje]

    #facturacion por especialidad
    fac_por_especialidad = df.groupby(['Especialidad'])['Monto Total'].sum().astype(int).sort_values(
        ascending=False)

    fac_por_especialidad = fac_por_especialidad.to_frame().assign(
        Porcentaje=lambda x: x['Monto Total'] / total_facturacion * 100).round(2)

    grafico_fac_por_especialidad = make_subplots(rows=1, cols=1)
    grafico_fac_por_especialidad.add_trace(
        go.Bar(x=fac_por_especialidad.index,
               y=fac_por_especialidad['Monto Total'],
               marker=dict(color='#16c2d5'),
               text=fac_por_especialidad['Monto Total'].apply(lambda x: "<b>${:,.0f}<b>".format(x)),
               textposition='auto'))

    grafico_fac_por_especialidad.update_layout(
        title='Facturación por Especialidad',
        xaxis_title='Centro',
        yaxis_title='Monto Total'
    )

    fac_por_especialidad.loc['Total'] = [total_facturacion, total_porcentaje]

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
            Media_estudio=lambda x: x['Monto Total'] / x['Cantidad'])
        monto_por_especialidad = monto_por_especialidad.fillna(0)
        monto_por_especialidad['Media_estudio'] = monto_por_especialidad['Media_estudio'].astype(int)

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





#SERVICIO MAMAS

    estudios_mamas = ['COLOCACIÓN DE CLIP INTRATUMORAL', 'DOPPLER GINECOLOGICO', 'DOPPLER MAMARIO',
                      'ECOGRAFIA MAMARIA UNI O BILATERAL', 'HISTEROSALPINGOGRAFIA VIRTUAL BAJO TCM',
                      'LOCALIZACION Y MARCACION MAMOGRAFICA', 'MAGNIFICACION', 'MAGNIFICACION BILATERAL',
                      'MAMOGRAFIA BILATERAL', 'MAMOGRAFÍA PROYECCIÓN AXILAR', 'MAMOGRAFÍA UNILATERAL',
                      'Marcación Prequirurgica de Mama (Ecografia)',
                      'Marcación Prequirurgica de Mama (Mamografia)',
                      'PUNCION BIOPSIA MAMARIA ASPIRATIVA GUIADA BAJO ECO',
                      'PUNCION BIOPSIA MAMARIA GUIADA BAJO ECOGRAFIA',
                      'PUNCION MAMARIA BAJO RMN CON SISTEMA DE VACIO', 'RM MAMARIA', 'RM MAMARIA BILATERAL',
                      'RX PIEZA OPERATORIA (Mamografia)', 'TAC MAMARIA', 'TECNICA DE EKLUND Bilateral',
                      'TECNICA DE EKLUND Unilateral']


    df_mamas = df[df['Practica'].isin(estudios_mamas)]
    df_mamas = df_mamas.groupby('Servicio')['Cantidad', 'Monto Total'].sum().astype(int).sort_values(by='Monto Total', ascending=False)


    total_monto_mamas = df_mamas['Monto Total'].sum()
    total_cantidad_mamas = df_mamas['Cantidad'].sum()

    df_mamas = df_mamas.assign(Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad_mamas * 100)
    df_mamas = df_mamas.assign(Porcentaje_monto=lambda x: x['Monto Total'] / total_monto_mamas * 100)

    df_mamas2 =  df[df['Practica'].isin(estudios_mamas)]
    df_mamas2 = df_mamas2.groupby('Practica')['Cantidad', 'Monto Total'].sum().astype(int).sort_values(by='Monto Total', ascending=False)

    fig_mamas = make_subplots(specs=[[{"secondary_y": True}]])

    fig_mamas.add_trace(go.Bar(x=df_mamas.index,
                         y=df_mamas['Cantidad'],
                         name='Cantidad',
                         marker_color='#176ba0',
                         opacity=1,
                         width=0.3,
                         offset=-0.3),
                  secondary_y=False)

    fig_mamas.add_trace(go.Bar(x=df_mamas.index,
                         y=df_mamas['Monto Total'],
                         name='Monto ($)',
                         marker_color='#1de4bd',
                         opacity=1,
                         width=0.3,
                         offset=0),
                  secondary_y=True)

    fig_mamas.update_layout(
        title='Cantidad y monto facturado Servicio de Mamas')

    fig_mamas2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig_mamas2.add_trace(go.Bar(x=df_mamas2.index,
                               y=df_mamas2['Cantidad'],
                               name='Cantidad',
                               marker_color='#176ba0',
                               opacity=1,
                               width=0.3,
                               offset=-0.3),
                        secondary_y=False)

    fig_mamas2.add_trace(go.Bar(x=df_mamas2.index,
                               y=df_mamas2['Monto Total'],
                               name='Monto ($)',
                               marker_color='#1de4bd',
                               opacity=1,
                               width=0.3,
                               offset=0),
                        secondary_y=True)

    fig_mamas2.update_layout(
        title='Cantidad y monto facturado Servicio de Mamas por Práctica')


    df_mamas.loc['Total'] = [total_cantidad_mamas, total_monto_mamas, total_porcentaje, total_porcentaje]
    df_mamas2.loc['Total'] = [total_cantidad_mamas, total_monto_mamas]

    df_mamas2 = df_mamas2.assign(Porcentaje_cantidad=lambda x: x['Cantidad'] / total_cantidad_mamas * 100)
    df_mamas2 = df_mamas2.assign(Porcentaje_monto=lambda x: x['Monto Total'] / total_monto_mamas * 100)
    df_mamas2 = df_mamas2.assign(Ratio=lambda x: x['Porcentaje_monto'] / x['Porcentaje_cantidad'])
    df_mamas2 =  df_mamas2.assign(Media_estudio=lambda x: x['Monto Total'] / x['Cantidad'])






# Grupo CTN
    # Grupo CTN
    medicos_ctn = df_sin_insumos[df_sin_insumos['Medico Derivante'].isin([
        'BARROSO DANIEL', 'BONFIGLIO PABLO', 'BONIFIGLIO PABLO',
        'DUARTE NICOLAS', 'DUARTE NICOLAS  S.', 'ENTRENA CARLOS',
        'ENTRENA NICOLAS', 'ESCOBAR DARIO E.', 'HERRERO VERONICA',
        'KREITMAN CLAUDIA', 'MALETTI FERNANDO', 'MANTILARO ESTEBAN',
        'SOLSONA SEBASTIAN'
    ])]

    tabla_ctn = medicos_ctn.groupby(['Medico Derivante', 'Especialidad', 'Obra Social']).agg(
        {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(by=['Medico Derivante', 'Monto Total'],
                                                               ascending=[True, False])
    tabla_ctn['Monto Total'] = tabla_ctn['Monto Total'].apply('$ {:,.0f}'.format)
    tabla_ctn = tabla_ctn.reset_index()

    total_fac_ctn = medicos_ctn['Monto Total'].sum()
    total_cant_ctn = medicos_ctn['Cantidad'].sum()

    total_fac_ctn_especialidad = medicos_ctn.groupby(['Especialidad']).agg(
        {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(by='Monto Total', ascending=False)

    total_por_medico_ctn = medicos_ctn.groupby(['Medico Derivante', 'Especialidad', 'Obra Social']).agg(
        {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(by='Monto Total', ascending=False)

    total_fac_ctn_especialidad['Monto Total'] = total_fac_ctn_especialidad['Monto Total'].apply('$ {:,.0f}'.format)
    total_fac_ctn_especialidad['Cantidad'] = total_fac_ctn_especialidad['Cantidad'].apply('{:,.0f}'.format)

    total_fac_ctn_especialidad.loc['Total'] = ['{:,.0f}'.format(total_cant_ctn), '$ {:,.0f}'.format(total_fac_ctn)]



#Grupo CIDEM
    grupo_cidem = ['AGHETONI GABRIELA', 'AGUILAR ZAPATA JUSTO', 'AGUIRRE EDGARD ADRIAN', 'AODASSIO MARIA SOLEDAD',
                   'BEGA GABRIEL', 'BOCCIO EDUARDO', 'BURGOS LUIS', 'CABRERA LORENA SOLEDAD',
                   'CAMACHO MARIELA', 'CASTELLO PAULINA', 'CENOZ ANA MARIA', 'CONCINA ANGELES',
                   'CURIONI MARCELA', 'DIBLASI ROMINA', 'DOMINGUEZ MARCELO', 'DURANDO RICARDO',
                   'ENCINA SILVIA ROXANA', 'FIORENTINI NIDIA', 'GONZALEZ LUCIA', 'KREMER ANNA',
                   'KREMER GABRIELA', 'KUGLER MARIELA', 'LOSILLA MARIA VANESA', 'MARTINEZ LUQUE EMILIO',
                   'MEDINA MARIA ISABEL', 'MERONIUC GRACIANA', 'MIELE FABIANA', 'MOLINA MARIEL',
                   'NIEVAS JACQUELINE', 'NUCCETELLI MARIA GRACIANA', 'PARODI GUILLERMO', 'PEREZ GUILLERMO'                                                       'PUGLISI LUCIA',
                   'RABINOWICZ SERGIO', 'RUBIOLO MARINA', 'SANCHEZ YESICA ANABEL',
                   'SILVEYRA PAOLA', 'STRAUSS EVELINA', 'TRUZZI LAURA', 'VILLANUEVA CABALLERO VICTOR',
                   'ZARATE MARIA NOELIA']
    medicos_derivanted_cidem = df_sin_insumos[df_sin_insumos['Medico Derivante'].isin(grupo_cidem)]

    tabla_cidem = medicos_derivanted_cidem.groupby(['Medico Derivante', 'Especialidad', 'Obra Social']).agg(
        {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(by=['Medico Derivante', 'Monto Total'],
                                                               ascending=[True, False])
    tabla_cidem['Monto Total'] = tabla_cidem['Monto Total'].apply('$ {:,.0f}'.format)
    tabla_cidem = tabla_cidem.reset_index()

    total_fac_cidem = medicos_derivanted_cidem['Monto Total'].sum()
    total_cant_cidem = medicos_derivanted_cidem['Cantidad'].sum()

    total_fac_cidem_especialidad = medicos_derivanted_cidem.groupby(['Especialidad']).agg(
        {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(by='Monto Total', ascending=False)

    total_por_medico_cidem = medicos_derivanted_cidem.groupby(['Medico Derivante', 'Especialidad', 'Obra Social']).agg(
        {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(by='Monto Total', ascending=False)

    total_fac_cidem_especialidad['Monto Total'] = total_fac_cidem_especialidad['Monto Total'].apply('$ {:,.0f}'.format)
    total_fac_cidem_especialidad['Cantidad'] = total_fac_cidem_especialidad['Cantidad'].apply('{:,.0f}'.format)

    total_fac_cidem_especialidad.loc['Total'] = ['{:,.0f}'.format(total_cant_ctn), '$ {:,.0f}'.format(total_fac_ctn)]
















    selection = st.sidebar.selectbox(" ",["Estadísticas Generales", "Estadísticas por Servicio", "Servicio de Mamas", "Médicos Derivantes"])

    if selection == 'Estadísticas por Servicio':
        st.write(f'Estas estadísticas generales abarcan desde el {min_date} hasta el {max_date}')

        selected_service = st.selectbox("Elegí un servicio:", servicios)

        st.header('Servicio de ' + selected_service)
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


        if st.button('Exportar a Excel', key=50):
            datos_por_md_dict[selected_service] = datos_por_md_dict[selected_service][datos_por_md_dict[selected_service]['Cantidad'] >= min_quantity]
            datos_por_md_dict[selected_service].to_excel(f'datos_por_md_{selected_service}.xlsx')


        st.plotly_chart(datos_por_md_grafico_dict[selected_service])

    if selection == 'Estadísticas Generales':
        st.header('Estadísticas generales')
        st.write(f'Estas estadísticas abarcan desde el {min_date} hasta el {max_date}')
        st.subheader('Facturación por Centro')
        st.dataframe(fac_por_centro.style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)
        if st.button('Exportar a Excel', key=500):
            fac_por_centro.to_excel('fac_po_centro.xlsx')
        st.plotly_chart(grafico_fac_por_centro)
        st.plotly_chart(grafico_fac_por_centro_pie)
        st.markdown('---')
        st.subheader('Facturación por Servicio')
        st.dataframe(fac_por_servicio.style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)
        if st.button('Exportar a Excel', key=600):
            fac_por_servicio.to_excel('fac_por_servicio.xlsx')
        st.plotly_chart(grafico_fac_por_servicio)
        st.plotly_chart(grafico_fac_por_servicio_pie)
        st.markdown('---')
        st.subheader('Facturación por Especialidad')
        st.dataframe(fac_por_especialidad.style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)
        if st.button('Exportar a Excel', key=700):
            fac_por_especialidad.to_excel('fac_por_especialidad.xlsx')
        st.plotly_chart(grafico_fac_por_especialidad)

    if selection == 'Servicio de Mamas':
        st.header("Servicio de Mamas")
        st.write(f'Estas estadísticas abarcan desde el {min_date} hasta el {max_date}')
        st.subheader("Servicio de Mamas por Servicio")
        st.dataframe(df_mamas.style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)
        st.plotly_chart(fig_mamas)
        st.subheader("Servicio de Mamas por Práctica")
        st.dataframe(df_mamas2.style.format({'Monto Total': "$ {:,.0f}",
                                                                             'Porcentaje_cantidad': "{:,.2f} %",
                                                                             'Cantidad': '{:,.0f}',
                                                                             'Porcentaje_monto': "{:,.2f} %",
                                                                             'Porcentaje': "{:,.2f} %",
                                                                             'Media_estudio': "$ {:,.0f}",
                                                                             'Cantidad':'{:,.0f}'}),
                     use_container_width=True)

        st.plotly_chart(fig_mamas2)

    if selection == 'Médicos Derivantes':
        seleccion2 = option_menu(
            menu_title='',
            options=['Buscador General por Nombre', 'CTN', 'CIDEM']
        )
        if seleccion2 == 'Buscador General por Nombre':

            medico_derivante = st.multiselect("Buscar por Medico Derivante:",
                                              pd.Series(df_sin_insumos['Medico Derivante'].unique()).sort_values())
            especialidad = st.multiselect("Buscar por Especialidad:",
                                          pd.Series(df_sin_insumos['Especialidad'].unique()).sort_values(),
                                          default=pd.Series(df_sin_insumos['Especialidad'].unique()).sort_values())

            filtered_df = df_sin_insumos[(df_sin_insumos['Medico Derivante'].isin(medico_derivante)) & (
                df_sin_insumos['Especialidad'].isin(especialidad))]

            grouped_df = filtered_df.groupby(['Especialidad', 'Obra Social']).agg(
                {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(
                by=['Especialidad', 'Monto Total'], ascending=[True, False])

            grouped_df['Monto Total'] = grouped_df['Monto Total'].apply('$ {:,.0f}'.format)

            st.dataframe(grouped_df, use_container_width=True)
            if st.button('Exportar a Excel', key=80000):
                grouped_df.to_excel('derivantes.xlsx')

        if seleccion2 == 'CTN':
            st.subheader('Grupo CTN por Especialidad')
            st.dataframe(total_fac_ctn_especialidad, use_container_width=True)
            if st.button('Exportar a Excel', key=70000):
                total_fac_ctn_especialidad.to_excel('ctnTotal.xlsx')
            st.subheader('Buscador:')

            medico_derivante_ctn = st.multiselect("Buscar por Medico Derivante:",
                                                  pd.Series(tabla_ctn['Medico Derivante'].unique()).sort_values(),
                                                  default=pd.Series(
                                                      tabla_ctn['Medico Derivante'].unique()).sort_values())
            especialidad2 = st.multiselect("Buscar por Especialidad:",
                                           pd.Series(df_sin_insumos['Especialidad'].unique()).sort_values(),
                                           default=pd.Series(df_sin_insumos['Especialidad'].unique()).sort_values())

            filtered_df2 = df_sin_insumos[(df_sin_insumos['Medico Derivante'].isin(medico_derivante_ctn)) & (
                df_sin_insumos['Especialidad'].isin(especialidad2))]

            grouped_df_ctn = filtered_df2.groupby(['Medico Derivante', 'Especialidad']).agg(
                {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(
                by=['Medico Derivante', 'Especialidad', 'Monto Total'], ascending=[True, True, False])

            grouped_df_ctn['Monto Total'] = grouped_df_ctn['Monto Total'].apply('$ {:,.0f}'.format)

            st.dataframe(grouped_df_ctn, use_container_width=True)
            if st.button('Exportar a Excel', key=60000):
                grouped_df_ctn.to_excel('ctn.xlsx')

        if seleccion2 == 'CIDEM':
            st.subheader('Grupo CIDEM por Especialidad')
            st.dataframe(total_fac_cidem_especialidad, use_container_width=True)
            if st.button('Exportar a Excel', key=700000):
                total_fac_cidem_especialidad.to_excel('cidemTotal.xlsx')
            st.subheader('Buscador:')

            medico_derivante_cidem = st.multiselect("Buscar por Medico Derivante:",
                                                  pd.Series(tabla_cidem['Medico Derivante'].unique()).sort_values(),
                                                  default=pd.Series(
                                                      tabla_cidem['Medico Derivante'].unique()).sort_values())
            especialidad3 = st.multiselect("Buscar por Especialidad:",
                                           pd.Series(df_sin_insumos['Especialidad'].unique()).sort_values(),
                                           default=pd.Series(df_sin_insumos['Especialidad'].unique()).sort_values())

            filtered_df3 = df_sin_insumos[(df_sin_insumos['Medico Derivante'].isin(medico_derivante_cidem)) & (
                df_sin_insumos['Especialidad'].isin(especialidad3))]

            grouped_df_cidem = filtered_df3.groupby(['Medico Derivante', 'Especialidad']).agg(
                {'Cantidad': 'sum', 'Monto Total': 'sum'}).sort_values(
                by=['Medico Derivante', 'Especialidad', 'Monto Total'], ascending=[True, True, False])

            grouped_df_cidem['Monto Total'] = grouped_df_cidem['Monto Total'].apply('$ {:,.0f}'.format)

            st.dataframe(grouped_df_cidem, use_container_width=True)
            if st.button('Exportar a Excel', key=60000):
                grouped_df_cidem.to_excel('cidem.xlsx')




