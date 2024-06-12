# streamlit_app.py
import webbrowser  # para abrir otras apps
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Creamos la cabecera
st.set_page_config(page_title="ATE-Alta nuevos proyectos", page_icon="🆕")
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

def main():
    st.sidebar.title("Menú")
    selection = st.sidebar.radio("Ir a", list(PAGES.keys()))

    page = PAGES[selection]
    if page == "puestos":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.puestos")
    elif page == "responsabilidad":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.responsabilidad")
    elif page == "role":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.role")
    elif page == "salario_base_xcategoria_xaño":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.salario_base_xcategoria_xaño")
    elif page == "turno":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.turno")
    elif page == "user":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.user")
    elif page == "usuario":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.usuario")
    elif page == "valoracion_definitiva":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.valoracion_definitiva")
    elif page == "valoracion_tecnica_pr":
        manage_table("ate-rrhh-2024.Ate_kaibot_2024.valoracion_tecnica_pr")

def manage_table(table_name):
    st.title(f"Gestión de {table_name.split('.')[-1].replace('_', ' ').title()}")
    action = st.radio("Acción", ["Ver", "Insertar", "Modificar", "Eliminar"])

    if action == "Ver":
        query = f"SELECT * FROM `{table_name}`"
        df = client.query(query).to_dataframe()
        st.dataframe(df)

    elif action == "Insertar":
        columns_query = f"SELECT column_name FROM `{table_name}`.INFORMATION_SCHEMA.COLUMNS"
        columns = [row["column_name"] for row in client.query(columns_query)]
        values = {}
        for column in columns:
            values[column] = st.text_input(f"Valor para {column}")
        if st.button("Insertar"):
            columns_str = ", ".join(columns)
            values_str = ", ".join([f"'{value}'" for value in values.values()])
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

