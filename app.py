import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de archivos
USUARIOS_FILE = "usuarios.csv"
DB_FILE = "seguimiento_serfor_4_0.csv"

# Inicialización de estado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Funciones

def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        usuarios_df = pd.read_csv(USUARIOS_FILE, dtype=str)
        usuarios_df = usuarios_df.fillna("")
        if "usuario" in usuarios_df.columns and "password" in usuarios_df.columns:
            return dict(zip(usuarios_df["usuario"].astype(str), usuarios_df["password"].astype(str)))
        else:
            st.warning("El archivo de usuarios existe pero no tiene las columnas esperadas. Se creará uno nuevo con credenciales iniciales.")
    default_usuarios = {
        "admin": "serfor2026",
        "usuario": "seguimiento"
    }
    usuarios_df = pd.DataFrame({
        "usuario": list(default_usuarios.keys()),
        "password": list(default_usuarios.values())
    })
    usuarios_df.to_csv(USUARIOS_FILE, index=False)
    return default_usuarios


def guardar_usuarios(usuarios_dict):
    usuarios_df = pd.DataFrame({
        "usuario": list(usuarios_dict.keys()),
        "password": list(usuarios_dict.values())
    })
    usuarios_df.to_csv(USUARIOS_FILE, index=False)


def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        data = {
            'Componente': [
                'Integración de Información',
                'Infraestructura Tecnológica',
                'Seguridad de Información',
                'Gestión del Cambio'
            ],
            'Tarea': [
                'Migración de BD',
                'Renovación de Servidores',
                'Implementación ISO 27001',
                'Capacitación Personal'
            ],
            'Estado': ['Pendiente', 'Pendiente', 'Pendiente', 'Pendiente'],
            'Avance': [0, 0, 0, 0],
            'Observaciones': ['', '', '', '']
        }
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False)
        return df


def mostrar_tablero(df):
    st.title("🌲 SEGUIMIENTO PLAN ACCIÓN SERFOR 4.0")
    st.info("Plataforma interactiva para el monitoreo de hitos y avances institucionales.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avance General", f"{df['Avance'].mean():.1f}%")
    with col2:
        st.metric("Tareas Completadas", len(df[df['Estado'] == 'Completado']))
    with col3:
        st.metric("Alertas Críticas", len(df[df['Estado'] == 'Crítico']))

    st.markdown("---")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📊 Progreso por Componente")
        fig_bar = px.bar(
            df,
            x="Tarea",
            y="Avance",
            color="Estado",
            hover_data=['Observaciones'],
            color_discrete_map={
                "Completado": "#27ae60",
                "En Proceso": "#f1c40f",
                "Crítico": "#e74c3c",
                "Pendiente": "#bdc3c7"
            }
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("📈 Distribución")
        fig_pie = px.pie(
            df,
            names='Estado',
            hole=0.4,
            color='Estado',
            color_discrete_map={
                "Completado": "#27ae60",
                "En Proceso": "#f1c40f",
                "Crítico": "#e74c3c",
                "Pendiente": "#bdc3c7"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📋 Detalle de Seguimiento")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Descargar Reporte Completo",
        data=csv,
        file_name="reporte_serfor_4_0.csv",
        mime="text/csv"
    )


# Página principal
st.set_page_config(page_title="SERFOR 4.0", layout="wide")

if not st.session_state.logged_in:
    st.title("Acceso al Tablero SERFOR 4.0")
    st.write("Ingrese su usuario y contraseña para ver el tablero.")

    usuarios = cargar_usuarios()

    with st.form(key="login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_button = st.form_submit_button("Ingresar")

    if login_button:
        if username in usuarios and usuarios[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Acceso concedido. Bienvenido/a.")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    usuarios = cargar_usuarios()
    st.sidebar.write(f"👤 Conectado como: {st.session_state.username}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    if st.session_state.username == "admin":
        with st.sidebar.expander("🔧 Administración de usuarios", expanded=True):
            st.markdown("**Agregar usuario**")
            new_user = st.text_input("Nombre de usuario", key="new_user")
            new_pass = st.text_input("Contraseña", type="password", key="new_pass")
            if st.button("Crear usuario", key="create_user"):
                if not new_user or not new_pass:
                    st.warning("Complete usuario y contraseña para crear un usuario.")
                elif new_user in usuarios:
                    st.warning("El usuario ya existe.")
                else:
                    usuarios[new_user] = new_pass
                    guardar_usuarios(usuarios)
                    st.success(f"Usuario '{new_user}' creado.")
                    st.experimental_rerun()

            st.markdown("---")
            st.markdown("**Editar o eliminar usuario**")
            selected_user = st.selectbox("Usuario", sorted(usuarios.keys()), key="select_user")
            updated_pass = st.text_input("Nueva contraseña", type="password", key="update_pass")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Guardar contraseña", key="save_pass"):
                    if not updated_pass:
                        st.warning("Ingrese una nueva contraseña.")
                    else:
                        usuarios[selected_user] = updated_pass
                        guardar_usuarios(usuarios)
                        st.success(f"Contraseña de '{selected_user}' actualizada.")
                        st.experimental_rerun()
            with col2:
                if st.button("Eliminar usuario", key="delete_user"):
                    if selected_user == "admin":
                        st.error("No se puede eliminar el usuario admin.")
                    else:
                        usuarios.pop(selected_user, None)
                        guardar_usuarios(usuarios)
                        st.success(f"Usuario '{selected_user}' eliminado.")
                        st.experimental_rerun()

    df = cargar_datos()
    mostrar_tablero(df)
