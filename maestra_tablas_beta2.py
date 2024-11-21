import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery

# Configuración de la página y credenciales de BigQuery
st.set_page_config(page_title="RRHH del Norte - Maestra de Tablas-beta2", page_icon="👨")
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)

# Proyecto y dataset en BigQuery
project_id = 'ate-rrhh-2024'
dataset_id = 'Ate_kaibot_2024'

# Encabezado de la aplicación
st.title("¡Bienvenido a RRHH del Norte! 👷")
st.header("Gestión de Tablas Maestras de Factores")

# Función para listar tablas en el dataset, ordenadas por nombre
def listar_tablas():
    query = f"""
        SELECT table_name 
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
        ORDER BY table_name
    """
    tables = client.query(query).result()
    return [row.table_name for row in tables]

# Función para seleccionar tabla y ver registros
def ver_tabla_seleccionada(table_name, order_by_column=None):
    # Si se especifica una columna para ordenar
    order_by_clause = f"ORDER BY {order_by_column}" if order_by_column else ""
    query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}` {order_by_clause} LIMIT 100"
    try:
        df = client.query(query).to_dataframe()
        st.dataframe(df)
        return df
    except Exception as e:
        st.error(f"Error al consultar la tabla: {e}")
        return None

# Función para insertar registros en una tabla
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
        try:
            columns_str = ", ".join(values.keys())
            values_str = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values.values()])
            insert_query = f"INSERT INTO `{project_id}.{dataset_id}.{table_name}` ({columns_str}) VALUES ({values_str})"
            client.query(insert_query)
            st.success("Registro insertado con éxito")
        except Exception as e:
            st.error(f"Error al insertar el registro: {e}")

# Función para actualizar registros en una tabla
# Función para actualizar registros en una tabla
def actualizar_registro(table_name, columns, record_id):
    st.write("**Formulario para actualizar un registro existente**")
    
    # Obtener los valores actuales del registro
    query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}` WHERE id = {record_id}"
    df = client.query(query).to_dataframe()
    
    if df.empty:
        st.error(f"No se encontró el registro con ID {record_id}.")
        return
    
    # Crear un diccionario con los valores actuales del registro
    current_values = df.iloc[0].to_dict()  # Tomamos el primer (y único) registro
    
    updated_values = {}
    
    # Mostrar un input para cada columna (excepto 'id')
    for column in columns:
        if column.name != "id":  # No permitir editar la clave primaria
            current_value = current_values.get(column.name, "")  # Obtener el valor actual
            if column.field_type == "STRING":
                updated_values[column.name] = st.text_input(
                    f"Nuevo valor para {column.name}",
                    value=current_value,  # Pre-cargamos el valor actual
                    key=column.name
                )
            elif column.field_type == "INTEGER":
                updated_values[column.name] = st.number_input(
                    f"Nuevo valor para {column.name}",
                    value=current_value if current_value is not None else 0,  # Pre-cargamos el valor actual
                    step=1,
                    key=column.name
                )
            elif column.field_type == "FLOAT":
                updated_values[column.name] = st.number_input(
                    f"Nuevo valor para {column.name}",
                    value=current_value if current_value is not None else 0.0,  # Pre-cargamos el valor actual
                    step=0.1,
                    key=column.name
                )
            elif column.field_type == "BOOLEAN":
                updated_values[column.name] = st.checkbox(
                    f"Nuevo valor para {column.name}",
                    value=current_value if current_value is not None else False,  # Pre-cargamos el valor actual
                    key=column.name
                )
            elif column.field_type == "TIMESTAMP":
                updated_values[column.name] = st.date_input(
                    f"Nuevo valor para {column.name}",
                    value=current_value if current_value is not None else "",
                    key=column.name
                )

    # Si el usuario presiona el botón de actualizar
    if st.button("Actualizar"):
        try:
            # Crear la consulta de actualización
            update_query = ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in updated_values.items()])
            update_sql = f"UPDATE `{project_id}.{dataset_id}.{table_name}` SET {update_query} WHERE id={record_id}"
            
            # Ejecutar la consulta de actualización
            client.query(update_sql)
            st.success("Registro actualizado con éxito")
        except Exception as e:
            st.error(f"Error al actualizar el registro: {e}")



# Función para eliminar registros de una tabla
def eliminar_registro(table_name, record_id):
    if st.button("Eliminar"):
        try:
            client.query(f"DELETE FROM `{project_id}.{dataset_id}.{table_name}` WHERE id={record_id}")
            st.success("Registro eliminado con éxito")
        except Exception as e:
            st.error(f"Error al eliminar el registro: {e}")

# Función para crear una nueva tabla
def crear_tabla_nueva():
    st.write("**Crear una nueva tabla**")
    table_name = st.text_input("Nombre de la nueva tabla")
    num_columns = st.number_input("Número de columnas", min_value=1, max_value=10, step=1)
    columns = []
    
    # Variable para la selección de factor y su etiqueta
    tipo_factor = st.selectbox(
        "Seleccione un tipo de factor", 
        ["Ninguno", 
         "Factores de formación", 
         "Factores de jerarquización o mando", 
         "Factores de responsabilidad", 
         "Factores de iniciativa o autonomía", 
         "Factores de Complejidad", 
         "Factores de Especialización Dificultad Técnica", 
         "Factores de Penosidad"
        ]
    )
    
    # Asignar la etiqueta correspondiente según la selección del tipo de factor
    if tipo_factor == "Factores de formación":
        etiqueta = "formacion"
    elif tipo_factor == "Factores de jerarquización o mando":
        etiqueta = "factor_jerarquizacion"
    elif tipo_factor == "Factores de responsabilidad":
        etiqueta = "factor_responsabilidad"
    elif tipo_factor == "Factores de iniciativa o autonomía":
        etiqueta = "factor_iniciativa"
    elif tipo_factor == "Factores de Complejidad":
        etiqueta = "factor_complejidad"
    elif tipo_factor == "Factores de Especialización Dificultad Técnica":
        etiqueta = "dificultad_tecnica"
    elif tipo_factor == "Factores de Penosidad":
        etiqueta = "factor_penosidad"
    else:
        etiqueta = None  # Ninguna etiqueta si "Ninguno" es seleccionado
    
    for i in range(num_columns):
        col_name = st.text_input(f"Nombre de la columna {i + 1}", key=f"col_name_{i}")
        col_type = st.selectbox(
            f"Tipo de dato de la columna {i + 1}",
            ["STRING", "INTEGER", "FLOAT", "BOOLEAN", "TIMESTAMP"],
            key=f"col_type_{i}"
        )
        # Convertir FLOAT a FLOAT64
        if col_type == "FLOAT":
            col_type = "FLOAT64"
        if col_name:
            columns.append((col_name, col_type))
    
    if st.button("Crear Tabla"):
        try:
            # Crear la tabla con la definición de las columnas
            cols_str = ", ".join([f"{name} {dtype}" for name, dtype in columns])
            query = f"CREATE TABLE `{project_id}.{dataset_id}.{table_name}` ({cols_str})"
            client.query(query)
            
            # Si se seleccionó una etiqueta, añadirla como metadato de la tabla
            if etiqueta:
                label_query = f"""
                    ALTER TABLE `{project_id}.{dataset_id}.{table_name}`
                    SET OPTIONS (
                        labels = [("tipo_factor", "{etiqueta}")]
                    )
                """
                client.query(label_query)

            st.success(f"Tabla '{table_name}' creada exitosamente con etiqueta '{etiqueta}'")
            st.experimental_rerun()  # Refrescar la aplicación
        except Exception as e:
            st.error(f"Error al crear la tabla: {e}")


# Menú lateral
st.sidebar.title("Opciones de Tabla")
opcion = st.sidebar.selectbox("Seleccione una opción", 
                               ["Ver tablas", "Insertar registro", "Actualizar registro", "Eliminar registro", "Crear nueva tabla"])

# Listar tablas y desplegar selectbox para selección
tablas = listar_tablas()
if tablas:
    tabla_seleccionada = st.sidebar.selectbox("Seleccione una tabla", tablas)
else:
    st.sidebar.warning("No hay tablas disponibles en este dataset.")

# Opciones de operación según selección del usuario
if opcion == "Ver tablas" and tabla_seleccionada:
    st.subheader(f"Tabla seleccionada: {tabla_seleccionada}")
    columnas = client.get_table(f"{project_id}.{dataset_id}.{tabla_seleccionada}").schema
    columnas_nombres = [col.name for col in columnas]
    columna_orden = st.selectbox("Ordenar por columna:", ["Ninguna"] + columnas_nombres)
    columna_orden = columna_orden if columna_orden != "Ninguna" else None
    ver_tabla_seleccionada(tabla_seleccionada, order_by_column=columna_orden)

elif opcion == "Insertar registro" and tabla_seleccionada:
    columnas = client.get_table(f"{project_id}.{dataset_id}.{tabla_seleccionada}").schema
    insertar_registro(tabla_seleccionada, columnas)

elif opcion == "Actualizar registro" and tabla_seleccionada:
    columnas = client.get_table(f"{project_id}.{dataset_id}.{tabla_seleccionada}").schema
    record_id = st.sidebar.number_input("Ingrese el ID del registro a actualizar", value=1, step=1)
    actualizar_registro(tabla_seleccionada, columnas, record_id)

elif opcion == "Eliminar registro" and tabla_seleccionada:
    record_id = st.sidebar.number_input("Ingrese el ID del registro a eliminar", value=1, step=1)
    eliminar_registro(tabla_seleccionada, record_id)

elif opcion == "Crear nueva tabla":
    crear_tabla_nueva()
