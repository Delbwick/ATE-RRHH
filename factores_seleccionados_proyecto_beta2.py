import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuración de la página de Streamlit
st.set_page_config(page_title="RRHH del Norte - Selección de Factores", page_icon="📊")
st.title("RRHH del Norte - Selección de Factores Específicos y de Destino-Manual preliminar")

# HTML y CSS para mostrar el texto con desplazamiento en un contenedor de 300px de altura
scrollable_text_html = """
<div style="width: 100%; max-height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
  2.	El contenido del salario público.
Cada empleado público (funcionario o personal laboral) puede cobrar una cantidad diferente, como consecuencia de la suma de los diferentes conceptos retributivos: retribuciones básicas -sueldo base, trienios-, y retribuciones complementarias -complemento de destino, complemento específico-. Sin perjuicio de otros complementos -por resultados en la gestión o productividad- o percepción de gratificaciones extraordinarias, en caso de que los hubiera. (art. 122 LEPV).
La valoración sólo determina el complemento de destino y el complemento específico, aunque del estudio de los puestos de trabajo se pueden extraer otras propuestas.
El grupo o categoría en el que se clasifica un determinado puesto de trabajo está vinculado a los requisitos de titulación para el acceso al puesto. Es decir, la titulación de la persona no tiene importancia, sino la exigida para el acceso al puesto.
Atendiendo a la clasificación del puesto le corresponderán unas retribuciones básicas-sueldo y trienios*-. 
Los importes correspondientes a doce mensualidades (para el periodo enero a diciembre de 2024) en concepto de retribuciones básicas, son los que se recogen a continuación :
* Los trienios están regulados por Udalhitz (art. 69). 
Grupo/subgrupo	Sueldo (euros)	Trienios (euros)
A1	15.922,80	612,84
A2	13.768,20	499,80
B	12.035,28	438,48
C1	10.337,52	378,36
C2	8.603,76	257,52
E	7.874,76	193,92


Y para cada una de las pagas extraordinarias de los meses de junio y diciembre (2024), en concepto de sueldo y	trienios, las siguientes cuantías:

Grupo/subgrupo	Sueldo 
(euros)	Trienios 
(euros)
A1	818,82 	31,53
A2	836,78	30,37
B	866,84	31,60
C1	744,56	27,21
C2	710,44	21,24
E	656,23	16,16

La Ley 11/2022, de 1 de diciembre, del Empleo Público Vasco, establece en su artículo 122, en relación con el complemento del puesto de trabajo:
3.	El complemento de destino se fijará anualmente en los Presupuestos Generales de la Comunidad Autónoma del País Vasco y será el correspondiente al puesto de trabajo que se desempeñe, de acuerdo con la estructura de niveles jerárquicos de responsabilidad que cada Administración Pública determine en función de sus facultades organizativas.
Para la asignación del nivel de complemento de destino se tendrán en cuenta:
•	Nivel de titulación exigido
•	Nivel de coordinación requerido por la relación jerárquica o funcional del puesto
•	Responsabilidad, iniciativa y autonomía en la toma de decisiones y en la adopción de medidas
•	Grado de complejidad de la información a procesar para el correcto desarrollo de las tareas propias del	puesto	de trabajo



4.	El mismo artículo de la ley recoge que, el complemento específico, que salvo norma o pacto en contrario será único por cada puesto de trabajo que tenga asignado, retribuye las condiciones especiales de cada puesto de trabajo:
•	Dificultad técnica especial.
•	Responsabilidad.
•	Dedicación.
•	Penosidad o peligrosidad.
•	Y cualquier otra condición que se produzca en el puesto de trabajo.
Podrá fijarse una cuantía por el factor de incompatibilidad cuando para el desempeño de determinados puestos se requiera una dedicación absoluta al servicio público.
En ningún caso podrá percibirse el complemento específico como retribución consolidada, quedando condicionado el desempeño efectivo del puesto en las condiciones valoradas.
Las Administraciones Públicas Vascas podrán asignar, en su caso, un complemento específico a todos los puestos de trabajo de su organización. 
Las cuantías del complemento de destino se fijarán en la norma presupuestaria de cada Administración pública vasca, de acuerdo con los criterios que reglamentariamente establezca el órgano correspondiente para su determinación.

</div>
"""
st.markdown(scrollable_text_html, unsafe_allow_html=True)

# Autenticación y cliente de BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Función para obtener proyectos desde BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto AS id, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{'id': row.id, 'nombre': row.nombre} for row in results]

# CRUD Functions
def insertar_datos(nombre_tabla, data):
    query = f"""
        INSERT INTO `{nombre_tabla}` ({', '.join(data.keys())})
        VALUES ({', '.join([f"'{v}'" for v in data.values()])})
    """
    client.query(query)

def actualizar_datos(nombre_tabla, row_id, data):
    set_clause = ", ".join([f"{k}='{v}'" for k, v in data.items()])
    query = f"""
        UPDATE `{nombre_tabla}`
        SET {set_clause}
        WHERE id = '{row_id}'
    """
    client.query(query)

def eliminar_datos(nombre_tabla, row_id):
    query = f"""
        DELETE FROM `{nombre_tabla}`
        WHERE id = '{row_id}'
    """
    client.query(query)

# Función para obtener datos de la tabla específica usando el nombre de la tabla
def obtener_datos_tabla(nombre_tabla):
    query = f"SELECT * FROM `{nombre_tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Sidebar para selección de proyectos
st.sidebar.title("Opciones de Proyecto")
st.sidebar.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)

# Obtener proyectos y configurar proyecto inicial
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]

# Obtener id_proyecto desde la URL si está disponible
id_proyecto_url = st.experimental_get_query_params().get('id_proyecto', [None])[0]
if id_proyecto_url:
    proyecto_inicial = next((proyecto['nombre'] for proyecto in proyectos if str(proyecto['id']) == id_proyecto_url), proyectos_nombres[0])
else:
    proyecto_inicial = proyectos_nombres[0]

# Crear el selectbox para proyectos en el sidebar
opcion_proyecto = st.sidebar.selectbox("Seleccione un Proyecto:", proyectos_nombres, index=proyectos_nombres.index(proyecto_inicial))

# Obtener el ID del proyecto seleccionado
id_proyecto_seleccionado = next((proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == opcion_proyecto), None)

# Mostrar ID de proyecto seleccionado para verificación
st.write(f"**ID del Proyecto Seleccionado**: {id_proyecto_seleccionado}")

# Obtener y mostrar datos de tablas específicas para el proyecto seleccionado
if id_proyecto_seleccionado:
    # Complementos específicos
    complementos_especificos = get_complementos_especificos(id_proyecto_seleccionado)
    if complementos_especificos:
        st.write("### Factores Específicos del Proyecto")
        for nombre_tabla in complementos_especificos:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_especifico = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            
            # Muestra el DataFrame y permite la edición en línea
            edited_df = st.experimental_data_editor(df_complemento_especifico)
            
            # Guardar los cambios en BigQuery si se detectan modificaciones
            if not edited_df.equals(df_complemento_especifico):
                for index, row in edited_df.iterrows():
                    row_data = row.to_dict()
                    if pd.isna(row_data.get("id")):  # Inserta si no existe id
                        insertar_datos(nombre_tabla, row_data)
                    else:
                        actualizar_datos(nombre_tabla, row_data["id"], row_data)

            # Formulario para insertar nuevos datos
            with st.form(f"form_insertar_{nombre_tabla}", clear_on_submit=True):
                st.write(f"Insertar nuevo registro en {nombre_tabla}")
                nuevo_registro = {col: st.text_input(col) for col in df_complemento_especifico.columns if col != 'id'}
                insertar_submit = st.form_submit_button("Insertar")
                
                if insertar_submit:
                    insertar_datos(nombre_tabla, nuevo_registro)
                    st.success("Registro insertado correctamente")

    else:
        st.write("No se encontraron complementos específicos para el proyecto seleccionado.")
    
    # Complementos de destino
    complementos_destino = get_complementos_destino(id_proyecto_seleccionado)
    if complementos_destino:
        st.write("### Factores de Destino del Proyecto")
        for nombre_tabla in complementos_destino:
            st.write(f"**Tabla: {nombre_tabla}**")
            df_complemento_destino = obtener_datos_tabla(f"ate-rrhh-2024.Ate_kaibot_2024.{nombre_tabla}")
            
            # Muestra el DataFrame y permite la edición en línea
            edited_df = st.experimental_data_editor(df_complemento_destino)
            
            # Guardar los cambios en BigQuery si se detectan modificaciones
            if not edited_df.equals(df_complemento_destino):
                for index, row in edited_df.iterrows():
                    row_data = row.to_dict()
                    if pd.isna(row_data.get("id")):  # Inserta si no existe id
                        insertar_datos(nombre_tabla, row_data)
 
