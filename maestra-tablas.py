# streamlit_app.py
import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import random

# Creamos la cabecera
st.set_page_config(page_title="RRHH del Norte - Maestra de tablas", page_icon="👨")
st.title("¡Bienvenido a RRHH del Norte! 👷")
st.header("Modificación (Insertar,modificar,eliminar) registros de tablas")

# Definir el color de fondo del encabezado
header_html = """
    <style>
        .header-container {
            background-color: #2596be; /* Color de fondo */
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 10px;
        }
    </style>
"""

# Agregar el HTML personalizado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)
st.markdown("<h2>Tablas de Factores - Maestras detalle</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Páginas de la aplicación y sus tablas correspondientes OJO LOS ID ALGUNOS VAN EN MAYUSUCULAS
PAGES_TABLES = {
    "Capacidades Necesarias": ("ate-rrhh-2024.Ate_kaibot_2024.capacidades_necesarias", "id_capacidades_necesarias"),
    "Complejidad": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad", "id_complejidad"),
    "Complejidad Técnica": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_tecnica", "id_complejidad_tecnica"),
    "Complejidad Territorial": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_territorial", "id_complejidad_territorial"),
    #"Complemento de Destino": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_de_destino", "id_complemento_destino"),
   # "Complemento Específico por Año - ELIMINAR": ("ate-rrhh-2024.Ate_kaibot_2024.complemento_específico_xaño", "id_complemento_especifico"),
    "Condiciones de Trabajo": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    "Conocimientos básicos de acceso al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_basicos_acceso_al_puesto", "id_conocimientos_basicos"),
    "Conocimientos específicos al puesto": ("ate-rrhh-2024.Ate_kaibot_2024.conocimientos_especificos", "id_conocimientos_especificos"),
   # "Definitivo?¿ ": ("ate-rrhh-2024.Ate_kaibot_2024.definitivo", "id_definitivo"),
    "Esfuerzo Emocional": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_emocional", "id_esfuerzo"),
    "Esfuerzo Físico": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_fisico", "id_esfuerzo_fisico"),
    "Esfuerzo Mental": ("ate-rrhh-2024.Ate_kaibot_2024.esfuerzo_mental", "id_esfuerzo_mental"),
    "ACTUALIZACIÓN DE CONOCIMIENTOS /ESPECIALIZACIÓN/FICICULTAD TÉCNICA": ("ate-rrhh-2024.Ate_kaibot_2024.especializacion", "id_especializacion"),
    "Formacion": ("ate-rrhh-2024.Ate_kaibot_2024.formacion", "id_formacion_general"),
    #"Idioma del Proyecto?¿": ("ate-rrhh-2024.Ate_kaibot_2024.idioma_de_proyecto", "id_idioma_proyecto"),
    "Idiomas del puesto": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas", "id_idiomas"),
    "Idiomas (Euskera)": ("ate-rrhh-2024.Ate_kaibot_2024.idiomas_euskera", "Id_idioma_euskera"),
    "Importancia Relativa": ("ate-rrhh-2024.Ate_kaibot_2024.importancia_relativa", "id_importancia"),
    #"Incompatibilidad": ("ate-rrhh-2024.Ate_kaibot_2024.incompatibilidad", "id_incompatibilidad"),
    "Iniciativa": ("ate-rrhh-2024.Ate_kaibot_2024.iniciativa", "id_iniciativa"),
    "Mando": ("ate-rrhh-2024.Ate_kaibot_2024.mando", "id_mando"),
    "Nivel de Formación": ("ate-rrhh-2024.Ate_kaibot_2024.nivel_de_fomacion", "id_formacion"),
    "Penosidad del Turno": ("ate-rrhh-2024.Ate_kaibot_2024.penosidad_turno", "id_penosidad"),
   # "Porcentajes Variables?¿": ("ate-rrhh-2024.Ate_kaibot_2024.porcentajes_variables", "id_porcentajes_variables"),
    "Proyectos": ("ate-rrhh-2024.Ate_kaibot_2024.proyecto", "id_proyecto"),
    "Puestos": ("ate-rrhh-2024.Ate_kaibot_2024.puestos", "id_puesto"),
    "Responsabilidad Relacional": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad"),
    #"Salario Base por Categoría y Año - TABLA CALCULADA?¿?": ("ate-rrhh-2024.Ate_kaibot_2024.salario_base_xcategoria_xaño", "id_salario_base"),
    "Turno": ("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno"),
    #tablas nuevas
    "Mando no cuantificado sobre personas": ("ate-rrhh-2024.Ate_kaibot_2024.mando_no_cuantificado_personas", "id_mando_no_cuantificado_personas"),
    "Mando Cuantificado sobre Personas": ("ate-rrhh-2024.Ate_kaibot_2024.mando_cuantificado_personas", "id_mando_cuantificado_personas"),
    "Autonomia, iniciativa, complejidad de la actividad": ("ate-rrhh-2024.Ate_kaibot_2024.autonomia_complejidad", "id_autonomia_complejidad"),
    "RESPONSABILIDAD DE LA ACTIVIDAD": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad", "id_responsabilidad_actividad"),
    "RESPONSABILIDAD DE LA ACTIVIDAD (PERJUICIOS)": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_perjuicios", "id_responsabilidad_actividad_perjuicios"),
    "RESPONSABILIDAD DE PERJUICIOS/INTERVENCIÓN SUBSANACIÓN": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_actividad_subsanacion", "id_responsabilidad_actividad_subsanacion"),
    "CONDICIONES DE TRABAJO FÍSICO": ("ate-rrhh-2024.Ate_kaibot_2024.condiciones_de_trabajo", "id_condiciones"),
    "RESPONSABILIDAD SOBRE USUARIOS DE RESIDENCIA": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_residencia", "id_responsabilidad_residencia"),
    "POLIVALENCIA": ("ate-rrhh-2024.Ate_kaibot_2024.polivalencia", "id_polivalencia"),
    "RESPONSABILIDAD PARCIAL SOBRE EL PRESUPUESTO": ("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad_presupuesto", "id_responsabilidad_presupuesto"),

    #fin tablas nuevas
    "Calendario-Jornada-Turno": ("ate-rrhh-2024.Ate_kaibot_2024.calendario_jornada-turno", "id_calendario_jornada_turno"),
    "Complejidad funcional": ("ate-rrhh-2024.Ate_kaibot_2024.complejidad_funcional", "id_complejidad_funcional"),
    "Documentos del Proyecto HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.project_document", "id_documento"),
    "Role HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.role", "id_role"),
    "User HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.user", "id_user"),
    "Usuario HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.usuario", "id_usuario"),
    "Cliente HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.client", "id_cliente"),
    "Empresa HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.company", "id_empresa"),
  #  "Calendario?¿?": ("ate-rrhh-2024.Ate_kaibot_2024.calendar", "id_calendario"),
    
    "Valoración complemento de destino por año HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.valoracion_destino_puntos_por_ano", "id_valoracion_destino"),
    "Complemento de destino por poryecto HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.complementos_de_destino_por_proyecto","id_proyecto"),
    "Valoración preliminar por poryecto HACER CONSULTA ESPECÏFICA": ("ate-rrhh-2024.Ate_kaibot_2024.valoracion_preliminar_por_proyecto","id_valoracion_preliminar")
    
    }

def add_custom_css():
    st.markdown("""
        <style>
            .stButton>button {
                color: white;
                background-color: #0073e6;
            }
            .stTitle {
                color: #0073e6;
                font-size: 2em;
                font-weight: bold;
            }
            .stDataFrame {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

# Obtener los nombres de tablas con un prefijo específico
def get_table_names_with_prefix(prefix):
    query = f"""
        SELECT table_name 
        FROM `ate-rrhh-2024.Ate_kaibot_2024.INFORMATION_SCHEMA.TABLES`
        WHERE table_name LIKE '{prefix}%'
    """
    result = client.query(query).result()
    return [row['table_name'] for row in result]

# Obtener el próximo ID disponible en la tabla
def get_next_id(table_name, id_column):
    query = f"SELECT MAX({id_column}) AS max_id FROM `{table_name}`"
    result = client.query(query).result()
    max_id = next(result)['max_id']
    next_id = max_id + 1 if max_id is not None else 1
    st.write(f"El próximo {id_column} disponible es: {next_id}")
    return next_id

# Manejar las operaciones con las tablas
def manage_table(table_name, id_column, action):
    st.title(f"Gestión de la tabla {table_name}")

    if action == "insertar":
        # Insertar registro
        fields = {
            "letra": st.text_input("Letra"),
            "descripcion": st.text_input("Descripción"),
            "porcentaje_de_total": st.number_input("Porcentaje del Total", min_value=0.0, max_value=100.0, step=0.1),
            "puntos": st.number_input("Puntos", min_value=0.0, step=0.1),
            "id_idioma_registro": st.number_input("id_idioma (1-ESp;2-EUS)", min_value=1, step=1)
        }

        if st.button("Insertar"):
            next_id = get_next_id(table_name, id_column)
            columns = [id_column] + list(fields.keys())
            values = [next_id] + list(fields.values())

            # Formatear la consulta
            columns_str = ", ".join(columns)
            values_str = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values])

            query = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({values_str})"
            st.write(f"Consulta a ejecutar: {query}")

            try:
                client.query(query).result()
                st.success("Registro insertado correctamente")
            except Exception as e:
                st.error(f"Error al insertar el registro: {e}")

    elif action == "modificar":
        # Modificar registro
        query = f"SELECT * FROM `{table_name}`"
        records = [dict(row) for row in client.query(query).result()]
        
        if records:
            selected_id = st.selectbox("Selecciona el ID del registro a modificar", [record[id_column] for record in records])
            selected_record = next(record for record in records if record[id_column] == selected_id)

            updated_record = {}
            for key, value in selected_record.items():
                if key != id_column:
                    if isinstance(value, int):
                        updated_record[key] = st.number_input(f"Nuevo valor para {key}", value=value)
                    elif isinstance(value, float):
                        updated_record[key] = st.number_input(f"Nuevo valor para {key}", value=value, format="%f")
                    else:
                        updated_record[key] = st.text_input(f"Nuevo valor para {key}", value)
                else:
                    updated_record[key] = value

            if st.button("Actualizar registro"):
                update_query = f"""
                    UPDATE `{table_name}`
                    SET {', '.join([f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}" for k, v in updated_record.items() if k != id_column])}
                    WHERE {id_column} = {selected_id}
                """
                try:
                    client.query(update_query).result()
                    st.success("Registro actualizado correctamente")
                except Exception as e:
                    st.error(f"Error al actualizar el registro: {e}")

    elif action == "eliminar":
        # Eliminar registro
        query = f"SELECT * FROM `{table_name}`"
        records = [dict(row) for row in client.query(query).result()]
        
        if records:
            selected_id = st.selectbox("Selecciona el ID del registro a eliminar", [record[id_column] for record in records])
            selected_record = next(record for record in records if record[id_column] == selected_id)

            st.write("Registro seleccionado para eliminar:", selected_record)

            if st.button("Eliminar registro"):
                delete_query = f"DELETE FROM `{table_name}` WHERE {id_column} = {selected_id}"
                try:
                    client.query(delete_query).result()
                    st.success("Registro eliminado correctamente")
                except Exception as e:
                    st.error(f"Error al eliminar el registro: {e}")

# Aplicación principal
def app():
    st.sidebar.title("Tablas de Factores")
    
    table_prefix = 'tabla_no_factor'
    available_tables = get_table_names_with_prefix(table_prefix)

    if not available_tables:
        st.write("No se encontraron tablas que comiencen con 'tabla_no_factor'.")
        return

    selected_table = st.sidebar.selectbox("Selecciona una tabla", available_tables)

    if selected_table:
        st.sidebar.write(f"Tabla seleccionada: {selected_table}")
        
        # Opciones de acciones: Insertar, Modificar, Eliminar
        actions = {
            "Insertar": st.sidebar.checkbox("Insertar"),
            "Modificar": st.sidebar.checkbox("Modificar"),
            "Eliminar": st.sidebar.checkbox("Eliminar")
        }

        if actions["Insertar"]:
            manage_table(selected_table, "id", "insertar")
        if actions["Modificar"]:
            manage_table(selected_table, "id", "modificar")
        if actions["Eliminar"]:
            manage_table(selected_table, "id", "eliminar")

# Ejecutar la aplicación
if __name__ == "__main__":
    app()
