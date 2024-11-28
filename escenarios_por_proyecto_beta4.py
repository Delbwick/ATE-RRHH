import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configurar la página de Streamlit
st.set_page_config(page_title="RRHH Cálculo de Puestos por Proyecto y por puesto ", page_icon="👥")
st.title("¡Bienvenido a RRHH! ")
st.header("¡Calcula los Salarios Por Poryecto!")

# HTML personalizado para el encabezado
header_html = """
    <style>
        .header-container {
            background-color: #2596be;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 10px;
        }
        .wide-line {
            width: 100%;
            height: 2px;
            background-color: #333333;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        h1, h2 {
            font-family: 'Arial', sans-serif;
            font-size: 17pt;
            text-align: left;
            color: #333333;
        }
        h3 {
            font-family: 'Arial', sans-serif;
            font-size: 14pt;
            text-align: center;
            color: #333333;
        }
        .cell {
            border: 1px solid black;
            padding: 10px;
            text-align: center;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        .header-cell {
            background-color: #e0e0e0;
            font-weight: bold;
            border: 1px solid black;
            padding: 10px;
            text-align: center;
        }
        .dataframe-cell {
            overflow-x: auto;
            overflow-y: auto;
            max-width: 100%;
            max-height: 200px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #2596be;
            color: white;
        }
        td {
            background-color: #f9f9f9;
        }
    </style>
"""

# Agregar el HTML personalizado al encabezado
st.markdown(header_html, unsafe_allow_html=True)

# Agregar la imagen (logo) y el texto al encabezado
st.markdown('<div class="header-container"><img class="logo" src="https://www.rrhhdelnorte.es/-_-/res/702f8fd0-46a5-4f0d-9c65-afb737164745/images/files/702f8fd0-46a5-4f0d-9c65-afb737164745/e0e4dc73-78c2-4413-b62c-250cbeea83fa/683-683/3b3822cd156fd081c427cc6b35617e4031b98c63" alt="Logo"></div>', unsafe_allow_html=True)
#st.write("Detalle de proyectos")



# Crear API client para BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Funciones reutilizables
def ejecutar_consulta(query):
    return client.query(query).result().to_dataframe()

def obtener_datos_por_proyecto(tabla, id_proyecto, id_puesto=None, columna_extra=None):
    condicion_puesto = f"AND id_puesto = {id_puesto}" if id_puesto else ""
    query = f"""
        SELECT DISTINCT {columna_extra if columna_extra else 'complementos_especificos'}
        FROM `{tabla}`
        WHERE id_proyecto = {id_proyecto} {condicion_puesto}
    """
    return ejecutar_consulta(query)

def obtener_tabla_y_calcular_puntos(tabla, columna_tabla, porcentaje_columna, titulo, key_prefix):
    if tabla != 'No disponible':
        st.subheader(f"{titulo}: {tabla}")
        df = obtener_datos_tabla(tabla)
        if not df.empty:
            st.dataframe(df)
            opciones = df.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
            seleccion = st.selectbox(f"Selecciona un valor para {tabla.split('.')[-1]}:", opciones, key=f"{key_prefix}_{tabla}")
            if seleccion:
                letra, _ = seleccion.split(" - ")
                puntos = df.query(f"letra == '{letra}'")['puntos'].values[0]
                porcentaje = st.number_input(f"% Peso para {titulo}:", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f"{key_prefix}_porcentaje")
                puntos_ajustados = puntos * (porcentaje / 100)
                return puntos_ajustados
    return 0

def calcular_sueldo_base(puestos_ids, categorias_sueldo_dict):
    sueldos = {}
    for puesto_id in puestos_ids:
        categoria = st.selectbox(f"Selecciona la categoría para el puesto {puesto_id}:", categorias_sueldo_dict.keys(), key=f"cat_{puesto_id}")
        sueldos[puesto_id] = categorias_sueldo_dict[categoria]
    return sueldos

# Función principal
def main():
    st.title('Gestión de Proyectos y Factores')
    st.sidebar.markdown("### Selecciona el proyecto")
    proyectos_df = ejecutar_consulta("SELECT id_projecto, nombre FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`")
    proyectos_nombres = proyectos_df['nombre'].tolist()
    proyecto_seleccionado = st.sidebar.selectbox("Selecciona un proyecto", proyectos_nombres)
    id_proyecto = proyectos_df.query(f"nombre == '{proyecto_seleccionado}'")['id_projecto'].values[0]

    puestos_df = obtener_datos_por_proyecto('ate-rrhh-2024.Ate_kaibot_2024.puestos', id_proyecto, columna_extra='id_puesto, descripcion')
    puestos_nombres = puestos_df['descripcion'].tolist()
    puestos_seleccionados = st.sidebar.multiselect("Selecciona los puestos", puestos_nombres)
    puestos_ids = puestos_df.query(f"descripcion in {puestos_seleccionados}")['id_puesto'].tolist()

    if id_proyecto and puestos_seleccionados:
        selecciones = {'especificos': [], 'destino': []}
        for descripcion in puestos_seleccionados:
            id_puesto = puestos_df.query(f"descripcion == '{descripcion}'")['id_puesto'].values[0]
            factores_df = obtener_datos_por_proyecto(
                'ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto', id_proyecto, id_puesto
            )
            for _, row in factores_df.iterrows():
                tabla_especificos = row['complementos_especificos']
                puntos_especificos = obtener_tabla_y_calcular_puntos(tabla_especificos, "complementos_especificos", "% Peso específico", "Factores Específicos", f"esp_{id_puesto}")
                selecciones['especificos'].append({'Puesto': descripcion, 'Puntos': puntos_especificos})

                tabla_destino = row['complementos_destino']
                puntos_destino = obtener_tabla_y_calcular_puntos(tabla_destino, "complementos_destino", "% Peso destino", "Factores Destino", f"dest_{id_puesto}")
                selecciones['destino'].append({'Puesto': descripcion, 'Puntos': puntos_destino})

        st.markdown("### Resumen de Selecciones")
        for tipo, data in selecciones.items():
            st.markdown(f"#### {tipo.capitalize()}")
            if data:
                df_resumen = pd.DataFrame(data)
                st.dataframe(df_resumen)
                st.markdown(f"**Total {tipo}:** {df_resumen['Puntos'].sum():.2f}")

        # Calcular sueldos
        categorias_sueldo = ejecutar_consulta("SELECT nombre_categoria, sueldo FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_categoria_sueldo_por_ano`")
        categorias_sueldo_dict = categorias_sueldo.set_index('nombre_categoria')['sueldo'].to_dict()
        sueldos_base = calcular_sueldo_base(puestos_ids, categorias_sueldo_dict)

        st.markdown("### Sueldos Totales")
        total_especificos = sum(item['Puntos'] for item in selecciones['especificos'])
        total_destino = sum(item['Puntos'] for item in selecciones['destino'])
        for puesto_id, sueldo_base in sueldos_base.items():
            sueldo_total = sueldo_base + total_especificos + total_destino
            st.markdown(f"Sueldo Total para el puesto {puesto_id}: {sueldo_total:.2f} euros")

main()

 
