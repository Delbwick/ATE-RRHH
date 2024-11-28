import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Función para obtener los proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    results = client.query(query).result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# Función para obtener los complementos para un proyecto
def get_complementos(id_proyecto, tipo_complemento):
    query = f"""
        SELECT {tipo_complemento}
        FROM `ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto`
        WHERE id_proyecto = {id_proyecto}
    """
    results = client.query(query).result()
    return [row[0] for row in results]

# Función para actualizar el porcentaje de importancia en BigQuery
def actualizar_porcentajes(id_proyecto, complementos, tipo_complemento, porcentajes):
    for complemento in complementos:
        porcentaje = porcentajes.get(complemento, 0)
        update_query = f"""
            UPDATE `ate-rrhh-2024.Ate_kaibot_2024.{tipo_complemento}_x_proyecto`
            SET porcentaje_importancia = {porcentaje}
            WHERE id_proyecto = {id_proyecto} AND {tipo_complemento} = '{complemento}'
        """
        client.query(update_query)

# Mostrar la interfaz de usuario
def mostrar_interfaz():
    # Obtener los proyectos
    proyectos = get_proyectos()
    proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
    proyecto_inicial = proyectos_nombres[0]  # Selección por defecto del primer proyecto

    # Crear el sidebar con el selectbox
    st.sidebar.title("Opciones")
    st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
    opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))

    # Obtener el ID del proyecto seleccionado
    id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

    # Mostrar el ID seleccionado en el sidebar (opcional para verificación)
    if id_proyecto_seleccionado:
        st.sidebar.write(f"ID del proyecto seleccionado: {id_proyecto_seleccionado}")

    # Mostrar los complementos de destino y específicos
    if id_proyecto_seleccionado:
        # Obtener complementos
        complementos_destino = get_complementos(id_proyecto_seleccionado, "complemento_destino")
        complementos_especificos = get_complementos(id_proyecto_seleccionado, "complemento_especifico")

        # Mostrar inputs para porcentajes
        st.subheader("Actualizar Porcentajes de Importancia")

        porcentajes = {}

        # Input para complementos de destino
        for complemento in complementos_destino:
            porcentaje = st.number_input(f"Porcentaje para {complemento} (Destino)", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
            porcentajes[complemento] = porcentaje

        # Input para complementos específicos
        for complemento in complementos_especificos:
            porcentaje = st.number_input(f"Porcentaje para {complemento} (Específico)", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
            porcentajes[complemento] = porcentaje

        # Botón para actualizar los porcentajes
        if st.button("Actualizar Porcentajes"):
            # Actualizar los porcentajes en BigQuery
            try:
                actualizar_porcentajes(id_proyecto_seleccionado, complementos_destino, "complemento_destino", porcentajes)
                actualizar_porcentajes(id_proyecto_seleccionado, complementos_especificos, "complemento_especifico", porcentajes)
                st.success("Porcentajes actualizados correctamente.")
            except Exception as e:
                st.error(f"Error al actualizar los porcentajes: {e}")
    else:
        st.write("Selecciona un proyecto para actualizar los complementos.")
    
# Llamar a la función para mostrar la interfaz
mostrar_interfaz()
