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
            background-color: #2596be; /* Color de fondo */
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
    h1 {
        font-family: 'Arial', sans-serif;
        font-size: 17pt;
        text-align: left;
        color: #333333;
    }
    h2 {
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
        margin-bottom: 20px; /* Margen inferior para toda la "tabla" */
    }
    .header-cell {
        background-color: #e0e0e0;
        font-weight: bold;
        border: 1px solid black;
        padding: 10px;
        text-align: center;
       
    }
    .dataframe-cell {
        overflow-x: auto;  /* Habilita scroll horizontal */
        overflow-y: auto;  /* Habilita scroll vertical */
        max-width: 100%;   /* Limita el ancho al 100% del contenedor */
        max-height: 200px; /* Limita la altura a 300px y habilita scroll */
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

# Funciones para BigQuery
def get_proyectos():
    query = """
        SELECT id_projecto, nombre
        FROM `ate-rrhh-2024.Ate_kaibot_2024.proyecto`
    """
    return client.query(query).result().to_dataframe()

def get_puestos(id_proyecto):
    query_ids = f"""
    SELECT DISTINCT id_puesto
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto}
    """
    ids_puestos = client.query(query_ids).result().to_dataframe()['id_puesto'].tolist()
    if ids_puestos:
        query_descripciones = f"""
        SELECT id_puesto, descripcion
        FROM `ate-rrhh-2024.Ate_kaibot_2024.puestos`
        WHERE id_puesto IN UNNEST({ids_puestos})
        """
        return client.query(query_descripciones).result().to_dataframe()
    return pd.DataFrame(columns=['id_puesto', 'descripcion'])

def get_factores_seleccionados(id_proyecto, id_puesto):
    query_especificos = f"""
    SELECT DISTINCT complementos_especificos
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    df_especificos = client.query(query_especificos).result().to_dataframe()

    query_destino = f"""
    SELECT DISTINCT complementos_destino
    FROM `ate-rrhh-2024.Ate_kaibot_2024.factores_seleccionados_x_puesto_x_proyecto`
    WHERE id_proyecto = {id_proyecto} AND id_puesto = {id_puesto}
    """
    df_destino = client.query(query_destino).result().to_dataframe()

    df_combined = pd.merge(df_especificos, df_destino, how='outer', left_on='complementos_especificos', right_on='complementos_destino')
    return df_combined.fillna('No disponible')

def obtener_datos_tabla(tabla):
    query = f"SELECT * FROM `{tabla}` LIMIT 100"
    return client.query(query).result().to_dataframe().fillna('No disponible')

# Aplicación Streamlit
st.title('Gestión de Proyectos y Factores')
# Mostrar el encabezado y línea separadora
st.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

# Selección de Proyecto
st.sidebar.markdown("### Selecciona el proyecto")
proyectos_df = get_proyectos()
proyectos_nombres = proyectos_df['nombre'].tolist()
index_seleccionado = st.sidebar.selectbox("Selecciona un proyecto", proyectos_nombres)
id_proyecto_seleccionado = proyectos_df.query(f"nombre == '{index_seleccionado}'")['id_projecto'].values[0]

# Selección de Puestos
st.sidebar.markdown("### Selecciona los Puestos de Trabajo")
puestos_df = get_puestos(id_proyecto_seleccionado)
puestos_descripciones = puestos_df['descripcion'].tolist()
selected_puestos = st.sidebar.multiselect("Selecciona los puestos", puestos_descripciones)

# Variable para almacenar las selecciones
selecciones_especificos = []
selecciones_destino = []
selected_puestos_ids = puestos_df.query(f"descripcion in {selected_puestos}")['id_puesto'].tolist()

if id_proyecto_seleccionado and selected_puestos:
    st.markdown(f"### Factores Seleccionados para el Proyecto {id_proyecto_seleccionado} {index_seleccionado}")

    for descripcion in selected_puestos:
        id_puesto = puestos_df.query(f"descripcion == '{descripcion}'")['id_puesto'].values[0]
        factores_df = get_factores_seleccionados(id_proyecto_seleccionado, id_puesto)

        if not factores_df.empty:
            st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
            st.write(f"Factores para el Puesto {id_puesto} ({descripcion})")

            for index, row in factores_df.iterrows():
                tabla_especificos = row['complementos_especificos']
                tabla_destino = row['complementos_destino']

                # Factores Específicos
                if tabla_especificos != 'No disponible':
                    st.subheader(f"Factores Específicos: {tabla_especificos}")
                    st.markdown(f"<div class='header-cell'><h3>{tabla_especificos}</h3></div>", unsafe_allow_html=True)
                    df_especificos = obtener_datos_tabla(tabla_especificos)
                    if not df_especificos.empty:
                        #st.write("Tabla de Factores Específicos")
                        #st.dataframe(df_especificos)

                        # Selección de un valor específico en dos columnas (75% y 25%)
                        opciones_especificos = df_especificos.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()

                        # Dividimos la UI en dos columnas
                        col1, col2 = st.columns([3, 1])  # 75% y 25%

                        with col1:
                            
                            st.write("Tabla de Factores Específicos")
                            st.dataframe(df_especificos)
                            #st.markdown(f"<div class='cell dataframe-cell'>{df_especificos.to_html(index=False)}</div>", unsafe_allow_html=True)
                            # Ajuste del DataFrame con scroll horizontal
                            #st.markdown(f"<div class='cell dataframe-cell'>{df_especificos.to_html(index=False)}</div>", unsafe_allow_html=True)
                            seleccion_especifico = st.selectbox(f"Selecciona un valor para {tabla_especificos.split('.')[-1]}:", opciones_especificos, key=f"especifico_{index}")

                        if seleccion_especifico:
                            selected_letra, selected_descripcion = seleccion_especifico.split(" - ")
                            puntos = df_especificos.query(f"letra == '{selected_letra}'")['puntos'].values[0]

                            # Input para porcentaje en la segunda columna
                            with col2:
                                st.markdown(f"<div class='header-cell'><b>Peso del complemento específico para {tabla_especificos}</b></div>", unsafe_allow_html=True)
                                #porcentaje_especifico = st.number_input(f"% {selected_descripcion}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_especifico_{index}')
                                porcentaje_especifico = st.number_input(f"%Peso del complemento específico para {tabla_especificos}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_especifico_{index}')


                            # Calcular puntos ajustados
                            puntos_ajustados = puntos * (porcentaje_especifico / 100)

                            # Mostrar resultado
                            #st.write(f"Seleccionaste la letra: {selected_letra} y la descripción: {selected_descripcion}")
                            st.write(f"Seleccionaste la letra: {selected_letra}")

                            st.write(f"Puntos originales: {puntos}")
                            st.write(f"Puntos ajustados (con {porcentaje_especifico}%): {puntos_ajustados:.2f}")
                            st.markdown(f"<div class='header-cell'><b>Total de puntos de complemento específico con el peso porcentual</b></div>", unsafe_allow_html=True)
                            #st.markdown(f"<div class='cell'>{puntos_destino_peso}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='cell'>{puntos_ajustados}</div>", unsafe_allow_html=True)
                            selecciones_especificos.append({'Puesto': descripcion, 'Letra': selected_letra, 'Descripción': selected_descripcion, 'Puntos': puntos_ajustados})
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores específicos {tabla_especificos}.")

                # Factores de Destino
                if tabla_destino != 'No disponible':
                    st.subheader(f"Factores de Destino: {tabla_destino}")
                    df_destino = obtener_datos_tabla(tabla_destino)
                    if not df_destino.empty:
                        st.write("Tabla de Factores de Destino")
                        st.dataframe(df_destino)

                        # Selección de un valor destino en dos columnas (75% y 25%)
                        opciones_destino = df_destino.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()

                        # Dividimos la UI en dos columnas
                        col1, col2 = st.columns([3, 1])  # 75% y 25%

                        with col1:
                            seleccion_destino = st.selectbox(f"Selecciona un valor para {tabla_destino.split('.')[-1]}:", opciones_destino, key=f"destino_{index}")

                        if seleccion_destino:
                            selected_letra_destino, selected_descripcion_destino = seleccion_destino.split(" - ")
                            puntos_destino = df_destino.query(f"letra == '{selected_letra_destino}'")['puntos'].values[0]

                            # Input para porcentaje en la segunda columna
                            with col2:
                                porcentaje_destino = st.number_input(f"% {selected_descripcion_destino}", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_destino_{index}')

                            # Calcular puntos ajustados
                            puntos_ajustados_destino = puntos_destino * (porcentaje_destino / 100)

                            # Mostrar resultado
                            #st.write(f"Seleccionaste la letra: {selected_letra_destino} y la descripción: {selected_descripcion_destino}")
                            st.write(f"Seleccionaste la letra: {selected_letra}")

                            st.write(f"Puntos originales: {puntos_destino}")
                            st.write(f"Puntos ajustados (con {porcentaje_destino}%): {puntos_ajustados_destino:.2f}")
                            selecciones_destino.append({'Puesto': descripcion, 'Letra': selected_letra_destino, 'Descripción': selected_descripcion_destino, 'Puntos': puntos_ajustados_destino})
                    else:
                        st.write(f"No se encontraron datos para la tabla de factores de destino {tabla_destino}.")


for descripcion in selected_puestos:
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.header(f"Resumen de Selecciones para el Puesto: {descripcion}")
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)

    
    # Mostrar complementos específicos
    df_especificos_resumen = pd.DataFrame([item for item in selecciones_especificos if item['Puesto'] == descripcion])
    if not df_especificos_resumen.empty:
        st.markdown("#### Complementos Específicos")
        st.table(df_especificos_resumen[['Letra', 'Descripción', 'Puntos']])
        
        # Sumar los puntos específicos
        total_puntos_especificos = df_especificos_resumen['Puntos'].sum()
        st.markdown(f"**Total de Puntos Específicos: {total_puntos_especificos:.2f}**")  # Mostrar la suma formateada
        
    # Mostrar complementos de destino
    df_destino_resumen = pd.DataFrame([item for item in selecciones_destino if item['Puesto'] == descripcion])
    if not df_destino_resumen.empty:
        st.markdown("#### Complementos de Destino")
        st.table(df_destino_resumen[['Letra', 'Descripción', 'Puntos']])
        
        # Sumar los puntos de destino
        total_puntos_destino = df_destino_resumen['Puntos'].sum()
        st.markdown(f"**Total de Puntos de Destino: {total_puntos_destino:.2f}**")  # Mostrar la suma formateada


    # Calcular sueldo total
    st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
    st.title("Cálculo de Sueldo Total")

    sueldo_categoria_puesto = {id_puesto: 2000 for id_puesto in selected_puestos_ids}  # Dummy values, replace with actual
    puntos_especifico_sueldo = sum(item['Puntos'] for item in selecciones_especificos)
    puntos_valoracion = sum(item['Puntos'] for item in selecciones_destino)

    for puesto_id in selected_puestos_ids:
        puesto_nombre = puestos_df.query(f"id_puesto == {puesto_id}")['descripcion'].values[0]
        sueldo = sueldo_categoria_puesto[puesto_id]
        
        sueldo_total_puesto = sueldo + puntos_especifico_sueldo + puntos_valoracion
        
        # Mostrar el cálculo para cada puesto
        st.markdown(f"<h1>Cálculo para el puesto: {puesto_nombre}</h1>", unsafe_allow_html=True)
        #st.write(f"Bruto Anual con Jornada Ordinaria: {sueldo} + {puntos_especifico_sueldo} + {puntos_valoracion} = {sueldo_total_puesto:.2f} euros")


#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤
    #CALUCLO DE SUELDOS v2
#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤
# Cálculo de Sueldo Total
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
#st.title("Cálculo de Sueldo Total")

sueldo_categoria_puesto = {id_puesto: 2000 for id_puesto in selected_puestos_ids}  # Dummy values, replace with actual
#calculo sueldo base por puesto
# Consulta para obtener las categorías de sueldo
query_categorias_sueldo = """
    SELECT nombre_categoria, sueldo
    FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_categoria_sueldo_por_ano`
"""

# Ejecutar la consulta para obtener las categorías de sueldo
query_job_categorias_sueldo = client.query(query_categorias_sueldo)
results_categorias_sueldo = query_job_categorias_sueldo.result()
df_categorias_sueldo = pd.DataFrame(data=[row.values() for row in results_categorias_sueldo], columns=[field.name for field in results_categorias_sueldo.schema])

# Convertir el DataFrame de categorías de sueldo en un diccionario para fácil acceso
categorias_sueldo_dict = df_categorias_sueldo.set_index('nombre_categoria')['sueldo'].to_dict()

# Crear un diccionario para almacenar el sueldo base de cada puesto según su categoría
sueldo_categoria_puesto = {}

# Iterar por los puestos seleccionados y asignarles el sueldo de la categoría correspondiente
for id_puesto in selected_puestos_ids:
    # Selectbox para elegir la categoría de sueldo
        st.markdown("<h2>Selecciona la Categoría para el Puesto</h2>", unsafe_allow_html=True)
        st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
        categoria_seleccionada = st.selectbox(
            f"Seleccione la categoría de sueldo para {puesto_nombre}",
            list(categorias_sueldo_dict.keys()),
            key=f"{puesto_id}_categoria"
        )
        
        # Obtener el sueldo de la categoría seleccionada
        sueldo = categorias_sueldo_dict[categoria_seleccionada]
        st.write(f"Sueldo: {sueldo}")
        
        # Almacenar el sueldo en la variable
        sueldo_categoria_puesto[puesto_id] = sueldo
# Mostrar el resultado para ver los sueldos asignados por puesto
st.write("Sueldo base por puesto:", sueldo_categoria_puesto)

#fin sueldo base
puntos_especifico_sueldo = sum(item['Puntos'] for item in selecciones_especificos)
puntos_valoracion = sum(item['Puntos'] for item in selecciones_destino)

for puesto_id in selected_puestos_ids:
    puesto_nombre = puestos_df.query(f"id_puesto == {puesto_id}")['descripcion'].values[0]
    sueldo = sueldo_categoria_puesto[puesto_id]
    
    sueldo_total_puesto = sueldo + puntos_especifico_sueldo + puntos_valoracion
    
    # Mostrar el cálculo para cada puesto
    #st.markdown(f"<h2>Cálculo para el puesto: {puesto_nombre}</h2>", unsafe_allow_html=True)
    #st.write(f"Bruto Anual con Jornada Ordinaria: {sueldo} + {puntos_especifico_sueldo} + {puntos_valoracion} = {sueldo_total_puesto:.2f} euros")

# --- NUEVO CÁLCULO AÑADIDO AQUÍ ---
st.markdown("<h2>Valoración para regla de 3 para tabla de complemento específico por Año (Variable) son 100 puntos -> 34.388,95 euros</h2>", unsafe_allow_html=True)

# Definir las variables base para el cálculo
puntos_base = 100
valor_base = 34388.95  # euros, deberías actualizarlo si es necesario obtener de la tabla

# Cálculo inicial del valor de puntos específicos para el proyecto
valor_punto_especifico_proyecto = (puntos_especifico_sueldo * valor_base) / puntos_base

# Input para que el usuario introduzca el valor de puntos específicos si es necesario modificar
# Si el usuario introduce un valor, sobreescribimos valor_punto_especifico_proyecto
valor_punto_especifico_proyecto = st.number_input('Introduce el número de puntos específicos del proyecto:',
                                                  min_value=1.0,
                                                  value=valor_punto_especifico_proyecto,
                                                  step=0.01)

# Cálculo ajustado del sueldo específico, utilizando el valor final de valor_punto_especifico_proyecto
sueldo_especifico_ajustado = (valor_punto_especifico_proyecto * valor_base) / puntos_base

# Cálculo de los puntos de destino
puntos_destino_peso_total = round(puntos_valoracion)
st.write(f"puntos valoracion redondeado destino: {puntos_destino_peso_total}")

# Construir la consulta SQL para obtener el complemento destino anual
query_valoracion_puntos = f"""
    SELECT complemento_destino_anual
    FROM `ate-rrhh-2024.Ate_kaibot_2024.valoracion_destino_puntos_por_ano`
    WHERE puntos_valoracion_destino = {puntos_destino_peso_total}
    LIMIT 1
"""

# Ejecutar la consulta
query_job = client.query(query_valoracion_puntos)
results = query_job.result()

# Procesar los resultados para obtener el complemento destino anual
puntos_valoracion_anual = None
for row in results:
    puntos_valoracion_anual = row.complemento_destino_anual

st.write(f"puntos valoracion complemento destino: {puntos_valoracion_anual}")
st.write(f"sueldo base: {sueldo}")
st.write(f"complemento especifico: {valor_punto_especifico_proyecto}")
st.write(f"complemento de destino: {puntos_valoracion_anual}")


# Cálculo final del sueldo total
if puntos_valoracion_anual:
    sueldo_total = sueldo + valor_punto_especifico_proyecto + puntos_valoracion_anual
    st.write(f"Sueldo total con complementos específicos y valoración destino: {sueldo_total:.2f} euros")
else:
    st.write("No se pudo obtener el complemento destino anual.")
    
# Continuación del código anterior...

# Mostrar el cálculo para cada puesto
st.markdown(f"<h2>Cálculo para el puesto: {puesto_nombre}</h2>", unsafe_allow_html=True)
st.write(f"Bruto Anual con Jornada Ordinaria: {sueldo} + {valor_punto_especifico_proyecto} + {puntos_valoracion} = {sueldo_total_puesto:.2f} euros")
st.markdown(f"Bruto Anual con Jornada Ordinaria:<div class='cell'>{sueldo_total_puesto}</div>", unsafe_allow_html=True)


# --- Cálculo de la modalidad de disponibilidad especial ---
# Selección de la modalidad de disponibilidad especial
modalidad_disponibilidad = st.selectbox(
    'Selecciona la modalidad de disponibilidad especial:',
    options=[
        'Ninguna',
        'Jornada ampliada (hasta 10%)',
        'Disponibilidad absoluta (hasta 15%)',
        'Jornada ampliada con disponibilidad absoluta (hasta 20%)'
    ]
)

# Inicialización del porcentaje según la modalidad seleccionada
porcentaje_disponibilidad = 0.0
if modalidad_disponibilidad == 'Jornada ampliada (hasta 10%)':
    porcentaje_disponibilidad = 10.0
elif modalidad_disponibilidad == 'Disponibilidad absoluta (hasta 15%)':
    porcentaje_disponibilidad = 15.0
elif modalidad_disponibilidad == 'Jornada ampliada con disponibilidad absoluta (hasta 20%)':
    porcentaje_disponibilidad = 20.0

# Calcular el sueldo con disponibilidad especial
for puesto_id in selected_puestos_ids:
    puesto_nombre = puestos_df.query(f"id_puesto == {puesto_id}")['descripcion'].values[0]
    sueldo = sueldo_categoria_puesto[puesto_id]
    
    sueldo_total_puesto = sueldo + puntos_especifico_sueldo + puntos_valoracion
    
    sueldo_bruto_con_complementos = sueldo + puntos_especifico_sueldo + puntos_valoracion
    if porcentaje_disponibilidad > 0:
        incremento_disponibilidad = sueldo_bruto_con_complementos * (porcentaje_disponibilidad / 100)
        sueldo_total_con_disponibilidad = sueldo_total_puesto + incremento_disponibilidad
        st.write(f"Con la modalidad '{modalidad_disponibilidad}' ({porcentaje_disponibilidad}%), el sueldo total ajustado es: {sueldo_total_con_disponibilidad:.2f} euros")
    else:
        st.write("No se ha aplicado ningún complemento de disponibilidad especial.")

# Mostrar la referencia a la última publicación oficial
st.markdown("<div class='wide-line'></div>", unsafe_allow_html=True)
st.markdown("Última publicación oficial: BOPV del 27 de febrero del 2024")





#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤
    #Fin CALUCLO DE SUELDOS v2
#≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤≤
    
 
