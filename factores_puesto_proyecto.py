import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import uuid
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Selector de Factores", layout="wide")

# Cliente de BigQuery
client = bigquery.Client()

def obtener_datos_bigquery(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}`"
    df = client.query(query).to_dataframe()
    return df

# Diccionario de tablas de factores de complemento de destino
PAGES_TABLES = {
    "Formación": ("ate-rrhh-2024.Ate_kaibot_2024.formacion", "id_formacion_general"),
    "Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    "Complejidad Técnica destino": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    "Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    "Autonomía-Iniciativa-Complejidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    "Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    "Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_de_fomacion", "id_formacion"),
    "Responsabilidad de la Actividad": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "Responsabilidad Relacional": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad"),
    "Mando no cuantificado sobre personas": ("ate-rrhh-2024.Ate_kaibot_2024.mando_no_cuantificado_personas", "id_mando_no_cuantificado_personas"),
    "Mando Cuantificado sobre Personas": ("ate-rrhh-2024.Ate_kaibot_2024.mando_cuantificado_personas", "id_mando_cuantificado_personas"),
    "Autonomia, iniciativa, complejidad de la actividad": ("ate-rrhh-2024.Ate_kaibot_2024.Ate_kaibot_2024.autonomia_complejidad", "id_autonomia_complejidad"),
    "RESPONSABILIDAD DE LA ACTIVIDAD_destino": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "RESPONSABILIDAD DE LA ACTIVIDAD (PERJUICIOS)_destino": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_perjuicios", "id_responsabilidad_actividad_perjuicios"),
    "RESPONSABILIDAD DE PERJUICIOS/INTERVENCIÓN SUBSANACIÓN_destino": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_subsanacion", "id_responsabilidad_actividad_subsanacion"),
    "POLIVALENCIA_destino": ("ate-rrhh-2024.Ate_kaibot_2024.polivalencia", "id_polivalencia"),
}

# Mostrar los checkboxes para seleccionar factores de complemento de destino
st.markdown("<h2>Selecciona los Factores de complemento de destino:</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
st.write("Selecciona los Factores de complemento de destino:")

selected_factores = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES.items():
    if st.checkbox(nombre_tabla):
        selected_factores.append((nombre_completo, id_tabla))
        # Obtener y mostrar la descripción de la tabla
        table = client.get_table(nombre_completo)
        descripcion = table.description
        st.write(f"Descripción de la tabla {nombre_tabla}: {descripcion}")

if selected_factores:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.write("Selecciona los valores específicos de las tablas seleccionadas:")

    valores_seleccionados = {}
    for nombre_completo, id_tabla in selected_factores:
        st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
        df = obtener_datos_bigquery(nombre_completo)
        if not df.empty:
            opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df.iterrows()]
            opciones.insert(0, 'Ninguno')

            seleccion = st.radio(f"Seleccione una opción para {nombre_completo.split('.')[-1]}:", opciones, key=f"radio_{id_tabla}")

            if seleccion != 'Ninguno':
                fila_seleccionada = df.loc[opciones.index(seleccion) - 1]
                valores_seleccionados[id_tabla] = fila_seleccionada[id_tabla]

    st.write("Valores seleccionados:")
    st.write(valores_seleccionados)

# Diccionario de tablas de factores de complemento específico
PAGES_TABLES_2 = {
    "Complejidad Técnica": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Condiciones de Trabajo": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    "Esfuerzo Emocional": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_emocional", "id_esfuerzo"),
    "Esfuerzo Físico": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_fisico", "id_esfuerzo_fisico"),
    "Esfuerzo Mental": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_mental", "id_esfuerzo_mental"),
    "ACTUALIZACIÓN DE CONOCIMIENTOS /ESPECIALIZACIÓN/FICICULTAD TÉCNICA": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Idiomas del puesto?": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas", "id_idiomas"),
    "Idiomas (Euskera)": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas_euskera", "Id_idioma_euskera"),
    "Importancia Relativa": ("ate-rrhh-2024.Ate_kaibot_2024.importancia_relativa", "id_importancia"),
    "Incompatibilidad": ("ate-rrhh-2024.Ate_kaibot_2024.incompatibilidad", "id_incompatibilidad"),
    "Penosidad del Turno": ("ate-rrhh-2024.Ate_kaibot_2024.penosidad_turno", "id_penosidad"),
    "Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno"),
    "RESPONSABILIDAD DE LA ACTIVIDAD": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "RESPONSABILIDAD DE LA ACTIVIDAD (PERJUICIOS)": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_perjuicios", "id_responsabilidad_actividad_perjuicios"),
    "RESPONSABILIDAD DE PERJUICIOS/INTERVENCIÓN SUBSANACIÓN": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_subsanacion", "id_responsabilidad_actividad_subsanacion"),
    "POLIVALENCIA": ("ate-rrhh-2024.Ate_kaibot_2024.polivalencia", "id_polivalencia"),
    "RESPONSABILIDAD PARCIAL SOBRE EL PRESUPUESTO": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_presupuesto", "id_responsabilidad_presupuesto"),
}

# Mostrar los checkboxes para seleccionar factores de complemento específico
st.markdown("<h2>Selecciona los Factores de complemento específico:</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
st.write("Selecciona los Factores de complemento específico:")

selected_factores_2 = []
for nombre_tabla, (nombre_completo, id_tabla) in PAGES_TABLES_2.items():
    if st.checkbox(nombre_tabla):
        selected_factores_2.append((nombre_completo, id_tabla))
        # Obtener y mostrar la descripción de la tabla
        table = client.get_table(nombre_completo)
        descripcion = table.description
        st.write(f"Descripción de la tabla {nombre_tabla}: {descripcion}")

if selected_factores_2:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.write("Selecciona los valores específicos de las tablas seleccionadas:")

    valores_seleccionados_2 = {}
    for nombre_completo, id_tabla in selected_factores_2:
        st.write(f"Tabla: {nombre_completo.split('.')[-1]}")
        df = obtener_datos_bigquery(nombre_completo)
        if not df.empty:
            opciones = [f"{row['descripcion']} ({row['letra']})" for index, row in df.iterrows()]
            opciones.insert(0, 'Ninguno')

            seleccion = st.radio(f"Seleccione una opción para {nombre_completo.split('.')[-1]}:", opciones, key=f"radio_{id_tabla}")

            if seleccion != 'Ninguno':
                fila_seleccionada = df.loc[opciones.index(seleccion) - 1]
                valores_seleccionados_2[id_tabla] = fila_seleccionada[id_tabla]

    st.write("Valores seleccionados:")
    st.write(valores_seleccionados_2)
