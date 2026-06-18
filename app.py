import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(
    page_title="Quiniela 909 Fase 1",
    page_icon="logo.ico",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .top1 {
        color: #00C853;
        margin: 0px;
        padding: 0px;
        font-weight: bold;
    }
    .top2 {
        color: #FFD600;
        margin: 0px;
        padding: 0px;
        font-weight: bold;
    }
    .top3 {
        color: #FF8C00;
        margin: 0px;
        padding: 0px;
        font-weight: bold;
    }
    .top4-plus {
        color: #FFFFFF;
        margin: 0px;
        padding: 0px;
    }
    .header-style {
        font-size: 16px;
        color: #888888;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        gap: 0px;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0px;
    }
    .stDivider {
        margin-top: 2px;
        margin-bottom: 2px;
    }
    div[data-testid="column"] {
        padding-top: 0px;
        padding-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# Conexion a Supabase
@st.cache_resource
def conectar_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = conectar_supabase()

# Obtener datos mas recientes
@st.cache_data(ttl=30)
def obtener_datos():
    response = supabase.table('QuinielaFase1')\
        .select('*')\
        .order('fecha_calificacion', desc=True)\
        .execute()
    
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        fecha_max = df['fecha_calificacion'].max()
        df = df[df['fecha_calificacion'] == fecha_max]
    
    return df

def obtener_tamano_fuente(pos):
    if pos <= 3:
        return 24
    elif pos <= 10:
        return 20 - ((pos - 4) * 0.5)
    else:
        return 16

st.title("Resultados de la Quiniela Fase 1")

# Boton para actualizar datos
col_titulo, col_boton = st.columns([3, 1])
with col_boton:
    if st.button("Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

try:
    df = obtener_datos()
    
    if df.empty:
        st.warning("No hay datos disponibles en la base de datos.")
    else:
        # Ordenar por puntos de mayor a menor
        df = df.sort_values(by='puntos', ascending=False).reset_index(drop=True)
        
        # Busqueda de participantes
        st.subheader("Buscar Participante")
        busqueda = st.text_input("Nombre del participante:")
        
        if busqueda:
            df_filtrado = df[df['nombre_participante'].str.contains(busqueda, case=False)]
            if df_filtrado.empty:
                st.warning("No se encontro ningun participante con ese nombre.")
            else:
                st.success(f"Se encontraron {len(df_filtrado)} participante(s)")
                for _, row in df_filtrado.iterrows():
                    pos = df[df['nombre_participante'] == row['nombre_participante']].index[0] + 1
                    col_pos, col_nombre, col_aciertos, col_puntos = st.columns([0.5, 3, 2, 2])
                    
                    with col_pos:
                        st.markdown(f'<p style="color: #FF8C00; font-size: 20px; font-weight: bold;">{pos}</p>', unsafe_allow_html=True)
                    with col_nombre:
                        st.markdown(f'<p style="color: #FF8C00; font-size: 20px; font-weight: bold;">{row["nombre_participante"]}</p>', unsafe_allow_html=True)
                    with col_aciertos:
                        st.markdown(f'<p style="color: #FF8C00; font-size: 20px; font-weight: bold;">Aciertos {row["aciertos"]}</p>', unsafe_allow_html=True)
                    with col_puntos:
                        st.markdown(f'<p style="color: #FF8C00; font-size: 20px; font-weight: bold;">{row["puntos"]} pts</p>', unsafe_allow_html=True)
            
            st.divider()
        
        # Resumen general
        col1, col2 = st.columns(2)
        
        with col1:
            total_partidos = df['total_partidos'].iloc[0] if not df.empty else 0
            st.metric("Total de Partidos", total_partidos)
        
        with col2:
            partidos_jugados = df['partidos_actuales'].iloc[0] if not df.empty else 0
            st.metric("Partidos Jugados", partidos_jugados)
        
        st.divider()
        
        # Tabla de posiciones
        st.subheader("Tabla de Posiciones")
        
        for pos, (_, row) in enumerate(df.iterrows(), 1):
            col_pos, col_nombre, col_aciertos, col_puntos = st.columns([0.5, 3, 2, 2])
            
            tamano = obtener_tamano_fuente(pos)
            
            if pos == 1:
                clase = "top1"
            elif pos == 2:
                clase = "top2"
            elif pos == 3:
                clase = "top3"
            else:
                clase = "top4-plus"
            
            with col_pos:
                st.markdown(f'<p class="{clase}" style="font-size: {tamano}px;">{pos}</p>', unsafe_allow_html=True)
            
            with col_nombre:
                st.markdown(f'<p class="{clase}" style="font-size: {tamano}px;">{row["nombre_participante"]}</p>', unsafe_allow_html=True)
            
            with col_aciertos:
                st.markdown(f'<p class="{clase}" style="font-size: {tamano}px;">Aciertos {row["aciertos"]}</p>', unsafe_allow_html=True)
            
            with col_puntos:
                st.markdown(f'<p class="{clase}" style="font-size: {tamano}px;">{row["puntos"]} pts</p>', unsafe_allow_html=True)
            
            st.divider()

except Exception as e:
    st.error(f"Error al conectar con Supabase: {e}")