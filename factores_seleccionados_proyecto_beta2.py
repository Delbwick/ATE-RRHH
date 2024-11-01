import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino")

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)

# Funciones para obtener datos de BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    return client.query(query).result().to_dataframe()

def get_complementos(id_proyecto, tipo):
    table = "complemento_especifico_x_proyecto" if tipo == "especifico" else "complemento_destino_x_proyecto"
    query = f"""
        SELECT {tipo}
        FROM `ate-rrhh-2024.Ate_kaibot_2024.{table}`
        WHERE id_proyecto = {id_proyecto}
    """
    return client.query(query).result().to_dataframe()

def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Crear el sidebar para selección de proyectos
proyectos = get_proyectos()
proyecto_nombres = proyectos['nombre'].tolist()
opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyecto_nombres)

id_proyecto = proyectos.loc[proyectos['nombre'] == opcion_proyecto, 'id'].values[0]

# Funciones de visualización y modificación de factores
st.sidebar.subheader("Modificar o Añadir Factores")

# Crear selectbox para factores específicos y destino con etiquetas
tipo_complemento = st.sidebar.selectbox(
    "Seleccione un tipo de complemento para añadir:",
    ("Factores de formación", "Factores de jerarquización o mando", 
     "Factores de responsabilidad", "Factores de iniciativa o autonomía",
     "Factores de Complejidad", "Factores de Especializacion Dificultad Técnica", 
     "Factores de Peligrosidad", "Factores de Penosidad")
)

etiqueta = ""
if tipo_complemento == "Factores de formación":
    etiqueta = "formacion"
elif tipo_complemento == "Factores de jerarquización o mando":
    etiqueta = "factor_jerarquizacion"
elif tipo_complemento == "Factores de responsabilidad":
    etiqueta = "factor_responsabilidad"
elif tipo_complemento == "Factores de iniciativa o autonomía":
    etiqueta = "factor_iniciativa"
elif tipo_complemento == "Factores de Complejidad":
    etiqueta = "factor_complejidad"
elif tipo_complemento == "Factores de Especializacion Dificultad Técnica":
    etiqueta = "dificultad_tecnica"
elif tipo_complemento == "Factores de Peligrosidad":
    etiqueta = "factor_peligrosidad"
elif tipo_complemento == "Factores de Penosidad":
    etiqueta = "factor_penosidad"

# Mostrar factores seleccionados con opciones de actualización o eliminación
def mostrar_y_editar_factores(id_proyecto, tipo):
    st.subheader(f"Factores {tipo.capitalize()} del Proyecto Seleccionado")
    complementos = get_complementos(id_proyecto, tipo)
    
    for _, row in complementos.iterrows():
        factor = row[tipo]
        col1, col2 = st.columns([2, 1])
        col1.write(factor)
        col2.selectbox("Acciones", ["Actualizar", "Eliminar"])

# Ejecutar la función para mostrar factores
mostrar_y_editar_factores(id_proyecto, "especifico")
mostrar_y_editar_factores(id_proyecto, "destino")

# Función para obtener nuevas opciones de factores basados en la categoría seleccionada
def obtener_factores_disponibles(etiqueta):
    query = f"""
        SELECT table_name
        FROM `ate-rrhh-2024.Ate_kaibot_2024.INFORMATION_SCHEMA.TABLE_OPTIONS`
        WHERE option_value LIKE '%"{etiqueta}"%'
    """
    return client.query(query).result().to_dataframe()

# Seleccionar y guardar factores
factores_disponibles = obtener_factores_disponibles(etiqueta)
seleccion_nuevos = st.multiselect("Seleccione factores adicionales:", factores_disponibles['table_name'].tolist())

def guardar_factores(tabla, id_proyecto, factores):
    registros = [{"id_proyecto": id_proyecto, "factor": factor} for factor in factores]
    df_registros = pd.DataFrame(registros)
    client.load_table_from_dataframe(df_registros, tabla).result()
    st.success("Los factores seleccionados se han guardado correctamente en BigQuery.")

# Botón para guardar selecciones de factores nuevos
if st.button("Guardar Factores Nuevos"):
    guardar_factores("nombre_de_tabla_seleccionada", id_proyecto, seleccion_nuevos)
