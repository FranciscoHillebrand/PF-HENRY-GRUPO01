# =======================================================
# 🏀 interfaz NBA con Logo y Modelo de Predicción (analitIQ)
# Base de Interfaz: modeloBinarioInterfazBienDecimoConEntrenamiento.py
# ESTILO: Interfaz modernizada con tema oscuro y colores de analitIQ
# LÓGICA: Se mantiene la lógica de carga de datos desde Excel y el modelo de Regresión Logística del Décimo.
# CORRECCIÓN: Se utiliza un DataFrame de Pandas para X_test para evitar el UserWarning de scikit-learn.
# =======================================================

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import os

# ==============================================
# 1️⃣ Configuración de Imagen y Globales
# ==============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas de los logos
LOGO_PATH_EMPRESA = os.path.join(BASE_DIR, "logo.png") # Logo de la empresa
LOGO_PATH_NBA = os.path.join(BASE_DIR, "NBAlogo.png")  # Logo de la NBA

# Rutas de los datos
MATRIZ_PATH = os.path.join(BASE_DIR, "matriz_entrenamiento_final.csv")
DATOS_NBA_PATH = os.path.join(BASE_DIR, "datos_nba_analizados_final_v4.xlsx")
SHEET_EQUIPOS = "Equipos"
SHEET_JUGADORES = "Jugadores"
SHEET_ARBITROS = "Arbitros_y_Victorias"

# Tamaños
TAMANO_LOGO_ESQUINA = (90, 70) # Original company logo (analitIQ)
TAMANO_LOGO_ESQUINA_NBA = (50, 100) # NBA logo - tall portrait format with correct proportions
TAMANO_LOGO_PORTADA = (150, 150)

# Variables de estado de la aplicación
seleccion = []  # Almacena [local, visitante, arbitro]
logo_empresa_referencia = None 
logo_nba_referencia = None     
logo_portada_referencia = None 

COLOR_FONDO_PRINCIPAL = "#0F1419"  # Deep dark background
COLOR_FONDO_FRAME = "#1A1E27"      # Slightly lighter frame background
COLOR_GOLD = "#D4A959"             # Primary gold accent (from analitIQ logo)
COLOR_GOLD_DARK = "#8B7638"        # Darker gold for contrast
COLOR_BLANCO = "#FFFFFF"           # White for text
COLOR_BOTON = "#D4A959"            # Gold buttons
COLOR_BOTON_TEXTO = "#0F1419"      # Dark text on gold buttons
COLOR_BORDE_FRAME = "#D4A959"      # Gold border
COLOR_TEXTO_PRIMARIO = "#FFFFFF"   # Primary text
COLOR_TEXTO_SECUNDARIO = "#B0B8C1" # Secondary text
COLOR_EXITO = "#4A9D6F"            # Green for positive (wins)
COLOR_ALERTA = "#E74C3C"           # Red for negative (losses)


# ==============================================
# 2️⃣ Carga y Preparación del Modelo
# ==============================================
def cargar_datos_y_entrenar_modelo():
    """Carga los datos de entrenamiento y entrena el modelo de Regresión Logística."""
    try:
        # Cargar matriz de entrenamiento
        matriz_df = pd.read_csv(MATRIZ_PATH)
        
        # 1. Preparar datos de entrenamiento (X) y objetivo (y)
        features = ['diff_strength', 'Localia', 'star_home_is_injured', 'star_away_is_injured', 'referee_effect']
        X_train = matriz_df[features].fillna(0) # Rellenar NaNs con 0 (manejo simple)
        y_train = matriz_df['Resultado_Real'] # 1 si gana el local, 0 si pierde
        
        # 2. Entrenar el modelo
        modelo = LogisticRegression()
        modelo.fit(X_train, y_train)
        
        return modelo
    except Exception as e:
        messagebox.showerror("Error de Carga/Entrenamiento", f"No se pudo cargar o entrenar el modelo: {e}")
        return None

# Cargar el modelo al inicio de la aplicación
modelo_regresion = cargar_datos_y_entrenar_modelo()

# Cargar datos de referencia de equipos, jugadores y árbitros
try:
    # Cargar datos desde el archivo Excel
    df_equipos = pd.read_excel(DATOS_NBA_PATH, sheet_name=SHEET_EQUIPOS)
    df_jugadores = pd.read_excel(DATOS_NBA_PATH, sheet_name=SHEET_JUGADORES)
    df_arbitros = pd.read_excel(DATOS_NBA_PATH, sheet_name=SHEET_ARBITROS)
    
    # Preprocesamiento de datos de equipos para acceso rápido
    df_equipos['PPA_Total'] = (df_equipos['promedio de puntos ANOTADOS de local'] + df_equipos['promedio de puntos ANOTADOS de visitante']) / 2
    
    # Crear un diccionario de equipos para fácil acceso
    equipos_dict = df_equipos.set_index('nickname (Punto 2)')['PPA_Total'].to_dict()
    equipos_id_dict = df_equipos.set_index('nickname (Punto 2)')['id team (Punto 2)'].to_dict()
    
    # Crear un diccionario de jugadores lesionados (solo MVP's para simplificar la simulación)
    mvp_lesionados = df_jugadores[df_jugadores['Jugador más valioso (Punto 9)'] == 'Sí']
    mvp_lesionados_dict = mvp_lesionados.set_index('Equipo más reciente')['Estado MVP (Punto 9)'].to_dict()
    
    # Lista de árbitros
    arbitros_list = sorted(df_arbitros['nombre arbitro (Punto 3)'].unique().tolist())
    arbitros_dict = df_arbitros.groupby(['nombre arbitro (Punto 3)', 'nombre equipo'])['número de victorias del equipo con este árbitro (Punto 6)'].sum().to_dict()

    NOMBRES_EQUIPOS = sorted(equipos_dict.keys())
    
except Exception as e:
    messagebox.showerror("Error de Carga de Datos", f"No se pudieron cargar los archivos de datos. Asegúrese de que '{DATOS_NBA_PATH}' existe y contiene las hojas correctas: {e}")
    NOMBRES_EQUIPOS = []
    equipos_dict = {}
    mvp_lesionados_dict = {}
    arbitros_list = []
    arbitros_dict = {}


# ==============================================
# 3️⃣ Funciones de Interfaz (Tema Oscuro Moderno)
# ==============================================

def cargar_logo(tipo="esquina", path=LOGO_PATH_EMPRESA):
    """Carga y redimensiona un logo según su uso (esquina o portada) - ESTILO MODERNO OSCURO."""
    global logo_empresa_referencia, logo_nba_referencia, logo_portada_referencia
    try:
        if path == LOGO_PATH_NBA:
            size = TAMANO_LOGO_ESQUINA_NBA  # Use tall portrait size for NBA
        elif tipo == "esquina":
            size = TAMANO_LOGO_ESQUINA
        elif tipo == "portada":
            size = TAMANO_LOGO_PORTADA
        # Se usa RGBA para manejar posible transparencia como en el Décimo
        logo = Image.open(path).convert("RGBA") 
        logo = logo.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(logo)
    except Exception as e:
        print(f"⚠️ No se pudo cargar el logo ({path}):", e)
        return None

def crear_frame_moderno(root, height=390, width=650): 
    """Crea el contenedor central oscuro, centrado, con borde dorado - ESTILO MODERNO."""
    frame = tk.Frame(
        root,
        bg=COLOR_FONDO_FRAME, 
        bd=0, 
        relief="flat",
        highlightbackground=COLOR_BORDE_FRAME, 
        highlightcolor=COLOR_GOLD,
        highlightthickness=2 
    )
    # Usamos .place con anchor="center" como en el Noveno
    frame.place(relx=0.5, rely=0.5, anchor="center", width=width, height=height)
    return frame

def configurar_header_con_logo(frame, titulo):
    """Configura el logo de NBA (izq) y el de la empresa (der) en el frame - ESTILO MODERNO."""
    global logo_empresa_referencia, logo_nba_referencia
    
    # Cargar logos (se hace en cada llamada para asegurar la referencia)
    logo_empresa_referencia = cargar_logo("esquina", LOGO_PATH_EMPRESA) 
    logo_nba_referencia = cargar_logo("esquina", LOGO_PATH_NBA) 

    header_frame = tk.Frame(frame, bg=COLOR_FONDO_FRAME, height=100)
    header_frame.pack(fill='x', padx=0, pady=0)
    
    # Gold accent line at top
    accent_line = tk.Frame(header_frame, bg=COLOR_GOLD, height=3)
    accent_line.pack(fill='x')
    
    # Content frame with padding
    content_frame = tk.Frame(header_frame, bg=COLOR_FONDO_FRAME)
    content_frame.pack(fill='x', padx=15, pady=12)
    
    # 1. Logo de la NBA (Izquierda)
    if logo_nba_referencia:
        tk.Label(content_frame, image=logo_nba_referencia, bg=COLOR_FONDO_FRAME).pack(side='left', padx=5)

    # 2. Logo de la Empresa (Derecha)
    if logo_empresa_referencia:
        tk.Label(content_frame, image=logo_empresa_referencia, bg=COLOR_FONDO_FRAME).pack(side='right', padx=5)

    # 3. Título Centrado - Gold text with modern styling
    titulo_frame = tk.Frame(content_frame, bg=COLOR_FONDO_FRAME)
    titulo_frame.pack(side='top', fill='x', expand=True) 

    tk.Label(titulo_frame, text=titulo,
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 14, "bold"), fg=COLOR_GOLD).pack(anchor='center')


# ==============================================
# 4️⃣ Funciones de Lógica del Modelo
# ==============================================

def calcular_factor_arbitro(local, visitante, arbitro_seleccionado):
    """Calcula el factor de sesgo del árbitro (Victorias Local - Victorias Visitante)."""
    
    # 1. Obtener victorias del local con el árbitro
    try:
        # La clave del diccionario es (nombre_arbitro, nombre_equipo)
        victorias_local = arbitros_dict.get((arbitro_seleccionado, local), 0)
    except:
        victorias_local = 0
        
    # 2. Obtener victorias del visitante con el árbitro
    try:
        victorias_visitante = arbitros_dict.get((arbitro_seleccionado, visitante), 0)
    except:
        victorias_visitante = 0

    # 3. Calcular el efecto
    referee_effect = victorias_local - victorias_visitante
    
    return referee_effect, victorias_local, victorias_visitante


def hacer_prediccion(local, visitante, arbitro_seleccionado, mvp_local_lesionado=False, mvp_visitante_lesionado=False):
    """Prepara las características y usa el modelo para predecir la probabilidad de victoria del local."""
    
    if modelo_regresion is None:
        return 0.5, 0.5, "Modelo no entrenado"

    # 1. Diff Strength (Fuerza Diferencial)
    ppa_local = equipos_dict.get(local, 100)
    ppa_visitante = equipos_dict.get(visitante, 100)
    # Usamos la normalización del Décimo: (PPA_Local - PPA_Visitante) / (PPA_Local + PPA_Visitante)
    diff_strength = (ppa_local - ppa_visitante) / (ppa_local + ppa_visitante) 

    # 2. Localia
    localia = 1.0 # Siempre 1.0 ya que local es 'Local'

    # 3. Lesiones del MVP - Ahora recibe como parámetros
    star_home_is_injured = 1.0 if mvp_local_lesionado else 0.0
    star_away_is_injured = 1.0 if mvp_visitante_lesionado else 0.0
    
    # 4. Efecto del Árbitro
    referee_effect, victorias_local, victorias_visitante = calcular_factor_arbitro(local, visitante, arbitro_seleccionado)
    
    # 5. Crear un DataFrame de Pandas con los nombres de las features ✅ CORRECCIÓN APLICADA
    features_data = {
        'diff_strength': [diff_strength],
        'Localia': [localia],
        'star_home_is_injured': [star_home_is_injured],
        'star_away_is_injured': [star_away_is_injured],
        'referee_effect': [referee_effect]
    }
    
    # X_test es ahora un DataFrame, manteniendo los nombres de las features que usó el modelo
    X_test = pd.DataFrame(features_data) 
    
    # 6. Predecir
    probabilidades = modelo_regresion.predict_proba(X_test)[0]
    prob_local = probabilidades[1] # Probabilidad de 1 (Gana Local)
    prob_visitante = probabilidades[0] # Probabilidad de 0 (Gana Visitante)
    
    # 7. Determinar el ganador
    ganador = local if prob_local > prob_visitante else visitante
    
    # Devolver probabilidades y datos adicionales para el resumen
    return prob_local, prob_visitante, ganador, {
        "diff_strength": diff_strength,
        "star_home_is_injured": star_home_is_injured,
        "star_away_is_injured": star_away_is_injured,
        "referee_effect": referee_effect,
        "victorias_local_arbitro": victorias_local,
        "victorias_visitante_arbitro": victorias_visitante
    }


# ==============================================
# 5️⃣ Vistas de la Aplicación (Tema Oscuro Moderno)
# ==============================================

def mostrar_portada():
    """Muestra la vista de portada con el logo central - ESTILO MODERNO OSCURO."""
    global logo_portada_referencia

    root = tk.Tk()
    root.title("TrueShot (analitIQ)")
    root.geometry("850x520") 
    root.configure(bg=COLOR_FONDO_PRINCIPAL)

    frame = crear_frame_moderno(root, height=450, width=500) 

    # Cargar logo central de la EMPRESA (como en el Noveno)
    logo_portada_referencia = cargar_logo("portada", LOGO_PATH_EMPRESA) 
    if logo_portada_referencia:
        tk.Label(frame, image=logo_portada_referencia, bg=COLOR_FONDO_FRAME).pack(pady=(40, 10))

    tk.Label(frame, text="Analizador de Probabilidades NBA \n TrueShot", 
             bg=COLOR_FONDO_FRAME, fg=COLOR_GOLD, 
             font=("Segoe UI", 18, "bold")).pack(pady=(0, 5))
    
    tk.Label(frame, text="Powered by analitIQ",
             bg=COLOR_FONDO_FRAME, fg=COLOR_TEXTO_SECUNDARIO, 
             font=("Segoe UI", 11, "italic")).pack(pady=(0, 5))
             
    tk.Label(frame, text='We turn data into smart decisions',
             bg=COLOR_FONDO_FRAME, fg=COLOR_TEXTO_SECUNDARIO, 
             font=("Segoe UI", 11, "italic")).pack(pady=(0, 20))

    def comenzar_seleccion():
        root.destroy()
        mostrar_seleccion_equipos()

    tk.Button(frame, text="Comenzar Análisis", 
              command=comenzar_seleccion,
              bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, 
              font=("Segoe UI", 12, "bold"), padx=20, pady=8,
              activebackground=COLOR_GOLD_DARK, activeforeground=COLOR_BOTON_TEXTO,
              relief="flat", cursor="hand2").pack(pady=30)
              
    tk.Label(frame, text="Herramienta basada en Regresión Logística y Features clave.", 
             bg=COLOR_FONDO_FRAME, fg=COLOR_TEXTO_SECUNDARIO, font=("Segoe UI", 9)).pack(pady=10)
    
    root.mainloop()


def mostrar_seleccion_equipos():
    """Muestra la vista para seleccionar los equipos y el árbitro - ESTILO MODERNO OSCURO."""
    global seleccion
    seleccion = [] # Limpiar selección
    
    root = tk.Tk()
    root.title("TrueShot (analitIQ) - Selección")
    root.geometry("900x720") 
    root.configure(bg=COLOR_FONDO_PRINCIPAL)

    frame = crear_frame_moderno(root, height=620, width=700) 
    
    configurar_header_con_logo(frame, "Selección de Partido y Árbitro")
    
    # Frame contenedor principal para las selecciones
    selector_container = tk.Frame(frame, bg=COLOR_FONDO_FRAME)
    selector_container.pack(pady=20, padx=20, fill='both', expand=True)
    
    selector_container.grid_columnconfigure(0, weight=1)
    selector_container.grid_columnconfigure(1, weight=1)
    selector_container.grid_columnconfigure(2, weight=1)
    
    # --- Selección Local ---
    local_label = tk.Label(selector_container, text="Equipo Local:", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 11, "bold"), fg=COLOR_GOLD)
    local_label.grid(row=0, column=0, padx=15, pady=10, sticky='ew')
    
    local_var = tk.StringVar(root)
    local_var.set(NOMBRES_EQUIPOS[0] if NOMBRES_EQUIPOS else "No hay datos")
    
    # Configuración de menú desplegable moderno
    local_menu = tk.OptionMenu(selector_container, local_var, *NOMBRES_EQUIPOS)
    local_menu.config(width=22, font=("Segoe UI", 10), bg="#2A2E37", fg=COLOR_BLANCO, 
                      activebackground=COLOR_GOLD, activeforeground=COLOR_BOTON_TEXTO,
                      highlightthickness=1, highlightbackground=COLOR_GOLD)
    local_menu.grid(row=1, column=0, padx=15, pady=10, sticky='ew')
    
    # --- Separador ---
    vs_label = tk.Label(selector_container, text="VS", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 16, "bold"), fg=COLOR_GOLD)
    vs_label.grid(row=1, column=1, padx=10, pady=10)
    
    # --- Selección Visitante ---
    visitante_label = tk.Label(selector_container, text="Equipo Visitante:", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 11, "bold"), fg=COLOR_GOLD)
    visitante_label.grid(row=0, column=2, padx=15, pady=10, sticky='ew')
    
    visitante_var = tk.StringVar(root)
    visitante_var.set(NOMBRES_EQUIPOS[1] if len(NOMBRES_EQUIPOS) > 1 else "No hay datos")
    
    visitante_menu = tk.OptionMenu(selector_container, visitante_var, *NOMBRES_EQUIPOS)
    visitante_menu.config(width=22, font=("Segoe UI", 10), bg="#2A2E37", fg=COLOR_BLANCO,
                          activebackground=COLOR_GOLD, activeforeground=COLOR_BOTON_TEXTO,
                          highlightthickness=1, highlightbackground=COLOR_GOLD)
    visitante_menu.grid(row=1, column=2, padx=15, pady=10, sticky='ew')

    # --- Selección de Árbitro ---
    arbitro_label = tk.Label(selector_container, text="Árbitro Principal:", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 11, "bold"), fg=COLOR_GOLD)
    arbitro_label.grid(row=2, column=0, columnspan=3, padx=15, pady=(20, 10), sticky='ew')
    
    arbitro_var = tk.StringVar(root)
    arbitro_var.set(arbitros_list[0] if arbitros_list else "No hay árbitros")
    
    arbitro_menu = tk.OptionMenu(selector_container, arbitro_var, *arbitros_list)
    arbitro_menu.config(width=50, font=("Segoe UI", 10), bg="#2A2E37", fg=COLOR_BLANCO,
                        activebackground=COLOR_GOLD, activeforeground=COLOR_BOTON_TEXTO,
                        highlightthickness=1, highlightbackground=COLOR_GOLD)
    arbitro_menu.grid(row=3, column=0, columnspan=3, padx=15, pady=10, sticky='ew')
    
    # --- MVP Local ---
    mvp_local_label = tk.Label(selector_container, text="MVP Local:", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 10, "bold"), fg=COLOR_GOLD)
    mvp_local_label.grid(row=4, column=0, padx=15, pady=(15, 5), sticky='w')
    
    mvp_local_var = tk.StringVar(root, value="Activo")
    
    mvp_local_frame = tk.Frame(selector_container, bg=COLOR_FONDO_FRAME)
    mvp_local_frame.grid(row=5, column=0, padx=15, pady=10, sticky='ew')
    
    def select_mvp_local(estado):
        mvp_local_var.set(estado)
        update_mvp_local_buttons()
    
    def update_mvp_local_buttons():
        current = mvp_local_var.get()
        btn_activo_local.config(bg=COLOR_GOLD if current == "Activo" else "#3A3F48", 
                               fg=COLOR_BOTON_TEXTO if current == "Activo" else COLOR_TEXTO_SECUNDARIO)
        btn_lesionado_local.config(bg=COLOR_GOLD if current == "Lesionado" else "#3A3F48",
                                  fg=COLOR_BOTON_TEXTO if current == "Lesionado" else COLOR_TEXTO_SECUNDARIO)
    
    btn_activo_local = tk.Button(mvp_local_frame, text="Activo", command=lambda: select_mvp_local("Activo"),
                                 font=("Segoe UI", 10, "bold"), padx=15, pady=6,
                                 relief="flat", cursor="hand2", activebackground=COLOR_GOLD)
    btn_activo_local.pack(side='left', padx=5)
    
    btn_lesionado_local = tk.Button(mvp_local_frame, text="Lesionado", command=lambda: select_mvp_local("Lesionado"),
                                    font=("Segoe UI", 10, "bold"), padx=15, pady=6,
                                    relief="flat", cursor="hand2", activebackground=COLOR_GOLD)
    btn_lesionado_local.pack(side='left', padx=5)
    
    update_mvp_local_buttons()
    
    # --- MVP Visitante ---
    mvp_visitante_label = tk.Label(selector_container, text="MVP Visitante:", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 10, "bold"), fg=COLOR_GOLD)
    mvp_visitante_label.grid(row=4, column=2, padx=15, pady=(15, 5), sticky='w')
    
    mvp_visitante_var = tk.StringVar(root, value="Activo")
    
    mvp_visitante_frame = tk.Frame(selector_container, bg=COLOR_FONDO_FRAME)
    mvp_visitante_frame.grid(row=5, column=2, padx=15, pady=10, sticky='ew')
    
    def select_mvp_visitante(estado):
        mvp_visitante_var.set(estado)
        update_mvp_visitante_buttons()
    
    def update_mvp_visitante_buttons():
        current = mvp_visitante_var.get()
        btn_activo_visitante.config(bg=COLOR_GOLD if current == "Activo" else "#3A3F48",
                                   fg=COLOR_BOTON_TEXTO if current == "Activo" else COLOR_TEXTO_SECUNDARIO)
        btn_lesionado_visitante.config(bg=COLOR_GOLD if current == "Lesionado" else "#3A3F48",
                                      fg=COLOR_BOTON_TEXTO if current == "Lesionado" else COLOR_TEXTO_SECUNDARIO)
    
    btn_activo_visitante = tk.Button(mvp_visitante_frame, text="Activo", command=lambda: select_mvp_visitante("Activo"),
                                     font=("Segoe UI", 10, "bold"), padx=15, pady=6,
                                     relief="flat", cursor="hand2", activebackground=COLOR_GOLD)
    btn_activo_visitante.pack(side='left', padx=5)
    
    btn_lesionado_visitante = tk.Button(mvp_visitante_frame, text="Lesionado", command=lambda: select_mvp_visitante("Lesionado"),
                                        font=("Segoe UI", 10, "bold"), padx=15, pady=6,
                                        relief="flat", cursor="hand2", activebackground=COLOR_GOLD)
    btn_lesionado_visitante.pack(side='left', padx=5)
    
    update_mvp_visitante_buttons()
    
    # --- Botones de navegación ---
    button_frame = tk.Frame(frame, bg=COLOR_FONDO_FRAME)
    button_frame.pack(pady=20)

    def on_analizar():
        local = local_var.get()
        visitante = visitante_var.get()
        arbitro = arbitro_var.get()
        mvp_local_lesionado = mvp_local_var.get() == "Lesionado"
        mvp_visitante_lesionado = mvp_visitante_var.get() == "Lesionado"
        
        if local == visitante:
            messagebox.showwarning("Error de Selección", "El equipo local y el visitante no pueden ser el mismo.")
            return

        seleccion.extend([local, visitante, arbitro])
        root.destroy()
        mostrar_resultados(local, visitante, arbitro, mvp_local_lesionado, mvp_visitante_lesionado)

    tk.Button(button_frame, text="Analizar Partido", 
              command=on_analizar,
              bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, 
              font=("Segoe UI", 11, "bold"), padx=15, pady=8,
              activebackground=COLOR_GOLD_DARK, activeforeground=COLOR_BOTON_TEXTO,
              relief="flat", cursor="hand2").pack(side='left', padx=10)
              
    tk.Button(button_frame, text="Volver al Inicio", 
              command=lambda: (root.destroy(), mostrar_portada()),
              bg=COLOR_TEXTO_SECUNDARIO, fg=COLOR_FONDO_PRINCIPAL, 
              font=("Segoe UI", 10), padx=12, pady=6,
              activebackground=COLOR_BLANCO,
              relief="flat", cursor="hand2").pack(side='left', padx=5)
              
    root.mainloop()


def mostrar_resultados(local, visitante, arbitro_seleccionado, mvp_local_lesionado=False, mvp_visitante_lesionado=False):
    """Muestra los resultados de la predicción y el resumen de los factores - ESTILO MODERNO OSCURO."""
    
    # 1. Hacer la predicción
    prob_local, prob_visitante, ganador, resumen_data = hacer_prediccion(local, visitante, arbitro_seleccionado, mvp_local_lesionado, mvp_visitante_lesionado)
    
    # 2. Configurar la vista
    root = tk.Tk()
    root.title("TrueShot (analitIQ) - Resultado")
    root.geometry("900x750")
    root.configure(bg=COLOR_FONDO_PRINCIPAL)

    frame = crear_frame_moderno(root, height=660, width=700) 

    configurar_header_con_logo(frame, "Probabilidad de Victoria")

    match_info = tk.Label(frame, text=f"{local} vs. {visitante}", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 14, "bold"), fg=COLOR_BLANCO)
    match_info.pack(pady=15)
             
    arbitro_info = tk.Label(frame, text=f"Árbitro: {arbitro_seleccionado}", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 9), fg=COLOR_TEXTO_SECUNDARIO)
    arbitro_info.pack(pady=(0, 15))

    # --- Probabilidades locales ---
    local_label = tk.Label(frame, text=f"Probabilidad {local}:", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 11), fg=COLOR_TEXTO_SECUNDARIO)
    local_label.pack(pady=(10, 5))
    
    local_prob_text = tk.Label(frame, text=f"{prob_local*100:.2f}%", 
             bg=COLOR_FONDO_FRAME, fg=COLOR_EXITO if prob_local > prob_visitante else COLOR_ALERTA,
             font=("Segoe UI", 32, "bold"))
    local_prob_text.pack(pady=(0, 15))
             
    # --- Probabilidades visitante ---
    visitante_label = tk.Label(frame, text=f"Probabilidad {visitante}:", 
             bg=COLOR_FONDO_FRAME, font=("Segoe UI", 11), fg=COLOR_TEXTO_SECUNDARIO)
    visitante_label.pack(pady=(10, 5))
    
    visitante_prob_text = tk.Label(frame, text=f"{prob_visitante*100:.2f}%", 
             bg=COLOR_FONDO_FRAME, fg=COLOR_EXITO if prob_visitante > prob_local else COLOR_ALERTA,
             font=("Segoe UI", 32, "bold"))
    visitante_prob_text.pack(pady=(0, 20))

    # ================================
    # ================================
    resumen_color_bg = "#1F3A2E" if ganador == local else "#3A1F1F"
    resumen_color_border = COLOR_EXITO if ganador == local else COLOR_ALERTA
    
    resumen_frame = tk.Frame(frame, bg=resumen_color_bg, 
                             relief=tk.FLAT, borderwidth=2,
                             highlightbackground=resumen_color_border,
                             highlightthickness=1)
    resumen_frame.pack(pady=15, padx=15, fill='x')
    
    # Add padding frame inside
    resumen_content = tk.Frame(resumen_frame, bg=resumen_color_bg)
    resumen_content.pack(padx=12, pady=12, fill='x')

    ganador_color = COLOR_EXITO if ganador == local else COLOR_ALERTA

    tk.Label(resumen_content, text=f"🏆 Favorito: {ganador.upper()}", 
             bg=resumen_color_bg, fg=ganador_color, font=("Segoe UI", 12, "bold")).pack(pady=8)

    # Mostrar factores con estilo mejorado
    tk.Label(resumen_content, text="FACTORES CLAVE:", 
             bg=resumen_color_bg, fg=COLOR_GOLD, font=("Segoe UI", 10, "bold", "underline")).pack(pady=(8, 5), anchor='w', padx=5)
             
    # Factor 1: Fuerza Diferencial
    tk.Label(resumen_content, 
        text=f"• Fuerza Diferencial: {resumen_data['diff_strength']:.4f}", 
        bg=resumen_color_bg, fg=COLOR_TEXTO_SECUNDARIO, font=("Segoe UI", 9)).pack(anchor='w', padx=15, pady=2)

    # Factor 2: Localía
    tk.Label(resumen_content, 
        text="• Localía: Ventaja para el equipo local", 
        bg=resumen_color_bg, fg=COLOR_TEXTO_SECUNDARIO, font=("Segoe UI", 9)).pack(anchor='w', padx=15, pady=2)

    # Factor 3 y 4: Lesiones
    lesiones_home = 'Sí' if resumen_data['star_home_is_injured'] == 1.0 else 'No'
    lesiones_away = 'Sí' if resumen_data['star_away_is_injured'] == 1.0 else 'No'
    tk.Label(resumen_content, text=f"• MVP Lesionado: {local} ({lesiones_home}) / {visitante} ({lesiones_away})", 
             bg=resumen_color_bg, fg=COLOR_TEXTO_SECUNDARIO, font=("Segoe UI", 9)).pack(anchor='w', padx=15, pady=2)

    # Factor 5: Sesgo Arbitral
    sesgo_texto = f"• Sesgo Arbitral: {resumen_data['referee_effect']:.0f} (V. Local: {resumen_data['victorias_local_arbitro']} / V. Visitante: {resumen_data['victorias_visitante_arbitro']})"
    tk.Label(resumen_content, text=sesgo_texto, 
             bg=resumen_color_bg, fg=COLOR_TEXTO_SECUNDARIO, font=("Segoe UI", 9)).pack(anchor='w', padx=15, pady=2)
    
    # Botones de navegación
    button_frame = tk.Frame(frame, bg=COLOR_FONDO_FRAME)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Nuevo Análisis", 
              command=lambda: (root.destroy(), mostrar_seleccion_equipos()),
              bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, 
              font=("Segoe UI", 10, "bold"), padx=12, pady=6,
              activebackground=COLOR_GOLD_DARK, activeforeground=COLOR_BOTON_TEXTO,
              relief="flat", cursor="hand2").pack(side='left', padx=10)
              
    tk.Button(button_frame, text="Volver al Inicio", 
              command=lambda: (root.destroy(), mostrar_portada()),
              bg=COLOR_TEXTO_SECUNDARIO, fg=COLOR_FONDO_PRINCIPAL, 
              font=("Segoe UI", 10), padx=12, pady=6,
              activebackground=COLOR_BLANCO,
              relief="flat", cursor="hand2").pack(side='left', padx=10)
              
    root.mainloop()

# ==============================================
# 6️⃣ Inicio de la Aplicación
# ==============================================

if __name__ == "__main__":
    # La aplicación comienza llamando a la función de portada
    mostrar_portada()
