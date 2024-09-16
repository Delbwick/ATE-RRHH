# Aplicación Streamlit
st.title('Gestión de Proyectos y Factores')

# Selección de Proyecto
st.markdown("<h2>Selecciona el proyecto que quieres calcular</h2>", unsafe_allow_html=True)
proyectos = get_proyectos()
proyectos_nombres = [proyecto['nombre'] for proyecto in proyectos]
index_seleccionado = st.selectbox("Selecciona un proyecto", proyectos_nombres)
id_proyecto_seleccionado = next(proyecto['id'] for proyecto in proyectos if proyecto['nombre'] == index_seleccionado)

# Obtener y seleccionar Puestos
puestos = get_puestos(id_proyecto_seleccionado)
puestos_descripciones = [puesto['descripcion'] for puesto in puestos]
selected_puesto = st.selectbox("Selecciona un puesto", puestos_descripciones)

# Obtener el ID del puesto seleccionado
id_puesto_seleccionado = next((puesto['id'] for puesto in puestos if puesto['descripcion'] == selected_puesto), None)

# Mostrar factores seleccionados para el proyecto y puesto
if id_proyecto_seleccionado and id_puesto_seleccionado:
    factores_df = get_factores_seleccionados(id_proyecto_seleccionado, id_puesto_seleccionado)

    if not factores_df.empty:
        st.write("Factores Seleccionados para el Proyecto y Puesto")
        st.dataframe(factores_df)
    else:
        st.write("No se encontraron factores para la selección.")
else:
    st.write("Selecciona un proyecto y un puesto para ver los factores.")
