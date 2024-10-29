import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página y credenciales de BigQuery
st.set_page_config(page_title="RRHH del Norte - Maestra de Tablas-beta2", page_icon="👨")
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)

project_id = 'ate-rrhh-2024'
dataset_id = 'Ate_kaibot_2024'

# Encabezado
st.title("¡Bienvenido a RRHH del Norte! 👷")
st.header("Gestión de Tablas Maestras de Factores")

# Función para listar tablas en el dataset
def listar_tablas():
    query = f"""
        SELECT table_name 
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
    """
    tables = client.query(query).result()
    return [row.table_name for row in tables]

# Función para seleccionar tabla y ver registros
def ver_tabla_seleccionada(table_name):
    query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}` LIMIT 100"
    df = client.query(query).to_dataframe()
    st.dataframe(df)
    return df

# Función para insertar registros
def insertar_registro(table_name, columns):
    st.write("**Formulario para insertar un nuevo registro**")
    values = {}
    for column in columns:
        col_type = column.field_type
        if col_type == "STRING":
            values[column.name] = st.text_input(f"Ingrese {column.name}")
        elif col_type == "INTEGER":
            values[column.name] = st.number_input(f"Ingrese {column.name}", value=0, step=1)
        elif col_type == "FLOAT":
            values[column.name] = st.number_input(f"Ingrese {column.name}", value=0.0, step=0.1)
    if st.button("Insertar"):
        columns_str = ", ".join(values.keys())
        values_str = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values.values()])
        insert_query = f"INSERT INTO `{project_id}.{dataset_id}.{table_name}` ({columns_str}) VALUES ({values_str})"
        client.query(insert_query)
        st.success("Registro insertado con éxito")

# Función para actualizar registros
def actualizar_registro(table_name, columns, record_id):
    st.write("**Formulario para actualizar un registro existente**")
    updated_values = {}
    for column in columns:
        if column.name != "id":
            value = st.text_input(f"Nuevo valor para {column.name}", key=column.name)
            updated_values[column.name] = value
    if st.button("Actualizar"):
        update_query = ", ".join([f"{k}='{v}'" for k, v in updated_values.items()])
        client.query(f"UPDATE `{project_id}.{dataset_id}.{table_name}` SET {update_query} WHERE id={record_id}")
        st.success("Registro actualizado")

# Función para eliminar registros
def eliminar_registro(table_name, record_id):
    if st.button("Eliminar"):
        client.query(f"DELETE FROM `{project_id}.{dataset_id}.{table_name}` WHERE id={record_id}")
        st.success("Registro eliminado")

# Función para crear una nueva tabla
def crear_tabla_nueva():
    st.write("**Crear una nueva tabla**")
    table_name = st.text_input("Nombre de la nueva tabla")
    num_columns = st.number_input("Número de columnas", min_value=1, max_value=10)
    columns = []
    for i in range(num_columns):
        col_name = st.text_input(f"Nombre de la columna {i + 1}")
        col_type = st.selectbox(f"Tipo de dato de la columna {i + 1}", ["STRING", "INTEGER", "FLOAT", "BOOLEAN", "TIMESTAMP"])
        columns.append((col_name, col_type))
    if st.button("Crear Tabla"):
        cols_str = ", ".join([f"{name} {dtype}" for name, dtype in columns])
        query = f"CREATE TABLE `{project_id}.{dataset_id}.{table_name}` ({cols_str})"
        client.query(query)
        st.success("Tabla creada exitosamente")

# Menú lateral
st.sidebar.title("Opciones de Tabla")
opcion = st.sidebar.selectbox("Seleccione una opción", ["Ver tablas", "Insertar registro", "Actualizar registro", "Eliminar registro", "Crear nueva tabla"])

# Despliegue de opciones en el sidebar
tablas = listar_tablas()
tabla_seleccionada = st.sidebar.selectbox("Seleccione una tabla", tablas)

if opcion == "Ver tablas":
    ver_tabla_seleccionada(tabla_seleccionada)

elif opcion == "Insertar registro":
    columns = client.get_table(f"{project_id}.{dataset_id}.{tabla_seleccionada}").schema
    insertar_registro(tabla_seleccionada, columns)

elif opcion == "Actualizar registro":
    columns = client.get_table(f"{project_id}.{dataset_id}.{tabla_seleccionada}").schema
    record_id = st.sidebar.number_input("Ingrese el ID del registro a actualizar", value=1)
    actualizar_registro(tabla_seleccionada, columns, record_id)

elif opcion == "Eliminar registro":
    record_id = st.sidebar.number_input("Ingrese el ID del registro a eliminar", value=1)
    eliminar_registro(tabla_seleccionada, record_id)

elif opcion == "Crear nueva tabla":
    crear_tabla_nueva()
