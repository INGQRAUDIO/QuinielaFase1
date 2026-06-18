import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from supabase import create_client, Client

st.set_page_config(
    page_title="Quiniela - Resultados",
    page_icon="logo.ico",
    layout="wide"
)

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

def obtener_clase(pos):
    if pos == 1:
        return "top1"
    elif pos == 2:
        return "top2"
    elif pos == 3:
        return "top3"
    else:
        return "top4-plus"

st.title("Resultados de la Quiniela")

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
                
                filas_busqueda = ""
                for _, row in df_filtrado.iterrows():
                    pos = df[df['nombre_participante'] == row['nombre_participante']].index[0] + 1
                    filas_busqueda += f"""
                        <tr style="color: #FF8C00; font-size: 20px; font-weight: bold;">
                            <td style="width:50px; text-align:center;">{pos}</td>
                            <td style="text-align:left;">{row['nombre_participante']}</td>
                            <td style="width:110px; text-align:center;">{row['aciertos']}</td>
                            <td style="width:100px; text-align:center;">{row['puntos']} pts</td>
                        </tr>
                    """
                
                html_busqueda = f"""
                <html>
                <head>
                    <style>
                        body {{
                            background-color: #0E1117;
                            font-family: Arial, sans-serif;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            table-layout: fixed;
                        }}
                        th {{
                            text-align: left;
                            padding: 8px 10px;
                            border-bottom: 2px solid #555555;
                            color: #888888;
                            font-size: 14px;
                            font-weight: bold;
                            white-space: nowrap;
                        }}
                        td {{
                            padding: 4px 10px;
                            border-bottom: 1px solid #333333;
                            white-space: nowrap;
                            overflow: hidden;
                            text-overflow: ellipsis;
                        }}
                    </style>
                </head>
                <body>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th style="width:50px; text-align:center;">#</th>
                                    <th style="text-align:left;">Participante</th>
                                    <th style="width:110px; text-align:center;">Aciertos</th>
                                    <th style="width:100px; text-align:center;">Puntos</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_busqueda}
                            </tbody>
                        </table>
                    </div>
                </body>
                </html>
                """
                
                components.html(html_busqueda, height=50 * len(df_filtrado) + 50, scrolling=True)
            
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
        
        filas_tabla = ""
        for pos, (_, row) in enumerate(df.iterrows(), 1):
            tamano = obtener_tamano_fuente(pos)
            clase = obtener_clase(pos)
            
            if clase == "top1":
                color = "#00C853"
            elif clase == "top2":
                color = "#FFD600"
            elif clase == "top3":
                color = "#FF8C00"
            else:
                color = "#FFFFFF"
            
            filas_tabla += f"""
                <tr style="color: {color}; font-size: {tamano}px; font-weight: {'bold' if pos <= 3 else 'normal'};">
                    <td style="width:50px; text-align:center;">{pos}</td>
                    <td style="text-align:left;">{row['nombre_participante']}</td>
                    <td style="width:110px; text-align:center;">{row['aciertos']}</td>
                    <td style="width:100px; text-align:center;">{row['puntos']} pts</td>
                </tr>
            """
        
        html_tabla = f"""
        <html>
        <head>
            <style>
                body {{
                    background-color: #0E1117;
                    font-family: Arial, sans-serif;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                }}
                th {{
                    text-align: left;
                    padding: 8px 10px;
                    border-bottom: 2px solid #555555;
                    color: #888888;
                    font-size: 14px;
                    font-weight: bold;
                    white-space: nowrap;
                }}
                td {{
                    padding: 4px 10px;
                    border-bottom: 1px solid #333333;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }}
                @media (max-width: 768px) {{
                    th {{
                        font-size: 12px;
                        padding: 6px 5px;
                    }}
                    td {{
                        padding: 3px 5px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th style="width:50px; text-align:center;">#</th>
                            <th style="text-align:left;">Participante</th>
                            <th style="width:110px; text-align:center;">Aciertos</th>
                            <th style="width:100px; text-align:center;">Puntos</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_tabla}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        components.html(html_tabla, height=40 * len(df) + 50, scrolling=True)

except Exception as e:
    st.error(f"Error al conectar con Supabase: {e}")