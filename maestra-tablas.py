# streamlit_app.py
import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import random

# Creamos la cabecera
st.set_page_config(page_title="ATE-Maestra de tablas", page_icon="🆕")
st.title("¡Bienvenido a ATE! 👷")
st.header("¡Empieza tu Proyecto!")

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
st.write("# Alta nuevo cliente")

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Páginas de la aplicación
PAGES = {
    "Puestos": "puestos",
    "Responsabilidad": "responsabilidad",
    "Role": "role",
    "Salario Base": "salario_base_xcategoria_xaño",
    "Turno": "turno",
    "User": "user",
    "Usuario": "usuario",
    "Valoración Definitiva": "valoracion_definitiva",
    "Valoración Técnica": "valoracion_tecnica_pr",
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

def get_next_id(table_name, id_column):
    query = f"SELECT MAX({id_column}) AS max_id FROM `{table_name}`"
    result = client.query(query).result()
    for row in result:
        max_id = row['max_id']
        return max_id + 1 if max_id is not None else 1

def get_id_proyecto():
    # Suponiendo que esta función obtiene el id_proyecto de alguna manera
    # Aquí se retorna un valor fijo para fines de demostración
    return random.randint(1, 1000)

def main():
    st.sidebar.title("Menú")
    selection = st.sidebar.radio("Ir a", list(PAGES.keys()))

    page = PAGES[selection]
    if page == "puestos":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.puestos", "id_puesto")
    elif page == "responsabilidad":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad", "id_responsabilidad")
    elif page == "role":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.role", "id_role")
    elif page == "salario_base_xcategoria_xaño":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.salario_base_xcategoria_xaño", "id_salario_base")
    elif page == "turno":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.turno", "id_turno")
    elif page == "user":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.user", "id_user")
    elif page == "usuario":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.usuario", "id_usuario")
    elif page == "valoracion_definitiva":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.valoracion_definitiva", "id_valoracion_definitiva")
    elif page == "valoracion_tecnica_pr":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.valoracion_tecnica_pr", "id_valoracion_tecnica_pr")

def manage_table(table_name, id_column):
    st.title(f"Gestión de {table_name.split('.')[-1].replace('_', ' ').title()}")
    action = st.radio("Acción", ["Ver", "Insertar", "Modificar", "Eliminar"])

    if action == "Ver":
        query = f"SELECT * FROM `{table_name}`"
        df = client.query(query).to_dataframe()
        st.dataframe(df)

    elif action == "Insertar":
        # Especifica los campos de la tabla, excluyendo el id autoincremental y id_proyecto
        fields = {
            "letra": st.text_input("Letra"),
            "descripcion": st.text_input("Descripción"),
            "porcentaje_del_total": st.number_input("Porcentaje del Total", min_value=0.0, max_value=100.0, step=0.1),
            "puntos": st.number_input("Puntos", min_value=0, step=1)
        }
        if st.button("Insertar"):
            next_id = get_next_id(table_name, id_column)
            id_proyecto = get_id_proyecto()
            columns = [id_column, "id_proyecto"] + list(fields.keys())
            values = [next_id, id_proyecto] + list(fields.values())
            columns_str = ", ".join(columns)
            values_str = ", ".join([f"'{value}'" if isinstance(value, str) else str(value) for value in values])
            query = f"""
                INSERT INTO `{table_name}` ({columns_str})
                VALUES ({values_str})
            """
            client.query(query)
            st.success("Registro insertado correctamente")

    elif action == "Modificar":
        st.warning("La funcionalidad de modificación no está implementada aún.")
        # Código para modificar un registro

    elif action == "Eliminar":
        st.warning("La funcionalidad de eliminación no está implementada aún.")
        # Código para eliminar un registro

if __name__ == "__main__":
    add_custom_css()
    main()
