import streamlit as st
import pandas as pd

# Función para obtener los factores seleccionados (placeholder)
def get_factores_seleccionados(id_proyecto, id_puesto):
    # Aquí podrías implementar la consulta a la base de datos para obtener los factores
    return pd.DataFrame()

# Función para obtener los datos de la tabla (placeholder)
def obtener_datos_tabla(tabla_nombre):
    # Aquí podrías implementar la consulta a la base de datos para obtener los datos de la tabla
    return pd.DataFrame({
        'letra': ['A', 'B', 'C'],
        'descripcion': ['Descripción A', 'Descripción B', 'Descripción C'],
        'puntos': [100, 200, 300]
    })

# Datos de ejemplo
puestos_df = pd.DataFrame({
    'id_puesto': [1, 2, 3],
    'descripcion': ['Puesto 1', 'Puesto 2', 'Puesto 3']
})

# ID de proyecto seleccionado (placeholder)
id_proyecto_seleccionado = 1

# Lista de selecciones para factores específicos y de destino
selecciones_especificos = []
selecciones_destino = []

# Selección de puestos
selected_puestos = st.multiselect("Selecciona uno o más puestos", puestos_df['descripcion'])

# Iterar sobre cada puesto seleccionado
for descripcion in selected_puestos:
    id_puesto = puestos_df.query(f"descripcion == '{descripcion}'")['id_puesto'].values[0]
    factores_df = get_factores_seleccionados(id_proyecto_seleccionado, id_puesto)

    if not factores_df.empty:
        st.write(f"Factores para el Puesto {id_puesto} ({descripcion})")

        for index, row in factores_df.iterrows():
            tabla_especificos = row['complementos_especificos']
            tabla_destino = row['complementos_destino']

            # Factores Específicos
            if tabla_especificos != 'No disponible':
                st.subheader(f"Factores Específicos: {tabla_especificos}")
                df_especificos = obtener_datos_tabla(tabla_especificos)
                if not df_especificos.empty:
                    # Organizar en dos columnas (75% para el dataframe, 25% para el input)
                    col1, col2 = st.columns([0.75, 0.25])

                    with col1:
                        st.write("Tabla de Factores Específicos")
                        st.dataframe(df_especificos)
                    
                    with col2:
                        # Selección de un valor específico
                        opciones_especificos = df_especificos.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                        seleccion_especifico = st.selectbox(f"Selecciona un valor para {tabla_especificos.split('.')[-1]}:", opciones_especificos, key=f"especifico_{index}")
                        if seleccion_especifico:
                            selected_letra, selected_descripcion = seleccion_especifico.split(" - ")
                            puntos = df_especificos.query(f"letra == '{selected_letra}'")['puntos'].values[0]
                            
                            # Input para porcentaje
                            porcentaje_especifico = st.number_input(f"Introduce el porcentaje para {selected_descripcion}:", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_especifico_{index}')
                            
                            # Calcular puntos ajustados
                            puntos_ajustados = puntos * (porcentaje_especifico / 100)
                            
                            # Mostrar resultado
                            st.write(f"Puntos originales: {puntos}")
                            st.write(f"Puntos ajustados (con {porcentaje_especifico}%): {puntos_ajustados:.2f}")
                            selecciones_especificos.append({'Puesto': descripcion, 'Letra': selected_letra, 'Descripción': selected_descripcion, 'Puntos': puntos_ajustados})
                else:
                    st.write(f"No se encontraron datos para la tabla de factores específicos {tabla_especificos}.")
            
            # Factores de Destino
            if tabla_destino != 'No disponible':
                st.subheader(f"Factores de Destino: {tabla_destino}")
                df_destino = obtener_datos_tabla(tabla_destino)
                if not df_destino.empty:
                    # Organizar en dos columnas (75% para el dataframe, 25% para el input)
                    col1, col2 = st.columns([0.75, 0.25])

                    with col1:
                        st.write("Tabla de Factores de Destino")
                        st.dataframe(df_destino)
                    
                    with col2:
                        # Selección de un valor destino
                        opciones_destino = df_destino.apply(lambda r: f"{r['letra']} - {r['descripcion']}", axis=1).tolist()
                        seleccion_destino = st.selectbox(f"Selecciona un valor para {tabla_destino.split('.')[-1]}:", opciones_destino, key=f"destino_{index}")
                        if seleccion_destino:
                            selected_letra_destino, selected_descripcion_destino = seleccion_destino.split(" - ")
                            puntos_destino = df_destino.query(f"letra == '{selected_letra_destino}'")['puntos'].values[0]
                            
                            # Input para porcentaje
                            porcentaje_destino = st.number_input(f"Introduce el porcentaje para {selected_descripcion_destino}:", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key=f'porcentaje_destino_{index}')
                            
                            # Calcular puntos ajustados
                            puntos_ajustados_destino = puntos_destino * (porcentaje_destino / 100)
                            
                            # Mostrar resultado
                            st.write(f"Puntos originales: {puntos_destino}")
                            st.write(f"Puntos ajustados (con {porcentaje_destino}%): {puntos_ajustados_destino:.2f}")
                            selecciones_destino.append({'Puesto': descripcion, 'Letra': selected_letra_destino, 'Descripción': selected_descripcion_destino, 'Puntos': puntos_ajustados_destino})
                else:
                    st.write(f"No se encontraron datos para la tabla de factores de destino {tabla_destino}.")
