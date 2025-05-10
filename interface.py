import sys
import collections.abc

if sys.version_info >= (3, 10):
    sys.modules['collections'].Mapping = collections.abc.Mapping

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
                             QScrollArea, QFrame, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from experta import *
from videoWidget import VideoWidget
import pandas as pd
import json
import random
import unidecode

class SongFact(Fact):
    pass

class UserSelections(Fact):
    pass

class MotorInferencia(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recomendaciones = []
    
    @Rule(
        UserSelections(
            emotion=MATCH.emotion,
            activity=MATCH.activity
        ),
        SongFact(
            emociones_relacionadas=MATCH.emociones,
            actividades_afines=MATCH.actividades,
            youtube_link=MATCH.youtube,
            spotify_link=MATCH.spotify,
            artista_banda=MATCH.artista,
            cancion=MATCH.cancion,
            genero=MATCH.genero
        ),
        TEST(lambda emotion, emociones: emotion in emociones),
        TEST(lambda activity, actividades: activity in actividades)
    )
    def agregar_recomendacion(self, artista, cancion, youtube, spotify, genero):
        self.recomendaciones.append({
            "artista": artista,
            "cancion": cancion,
            "youtube": youtube,
            "spotify": spotify,
            "genero": genero
        })

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Generador de Playlists")
        self.resize(800, 600)
        
        self.df = self.cargar_dataset()
        self.init_ui()
    
    def init_ui(self):
        # Configuración de colores
        main_bg = "#404040"        # Color principal de fondo
        frame_bg = "#525252"       # Fondo de los frames
        combo_bg = "#E0E0E0"      # Fondo claro para combobox
        combo_text = "#333333"    # Texto oscuro para combobox
        button_bg = "#4694b8"      # Azul para el botón principal
        button_hover = "#5AA5C8"   # Azul más claro para hover
        button_pressed = "#3A84A8" # Azul más oscuro para pressed
        
        # Estilo general de la aplicación
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {main_bg};
                color: #F0F0F0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            
            QScrollBar:vertical {{
                background: {frame_bg};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: #707070;
                min-height: 20px;
                border-radius: 5px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(15)
        
        # --- Controles superiores ---
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {frame_bg};
                border-radius: 8px;
            }}
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(15, 15, 15, 15)
        controls_layout.setSpacing(15)
        
        # Combo Emoción
        self.combo_emocion = QComboBox()
        self.combo_emocion.addItems(["alegria",
                                     "tristeza",
                                     "euforia",
                                     "tranquilidad",
                                     "melancolia",
                                     "nostalgia",
                                     "ansiedad",
                                     "energia",
                                     "romance",
                                     "desamor",
                                     "furia",
                                     "esperanza-optimismo",
                                     "soledad",
                                     "empoderamiento",
                                     "motivacion",
                                     "frustracion",
                                     "miedo",
                                     "deseo"])
        self.combo_emocion.setCurrentText("Emoción")
        self.combo_emocion.setStyleSheet(f"""
            QComboBox {{
                background-color: {combo_bg};
                color: {combo_text};
                border: 1px solid #B0B0B0;
                border-radius: 6px;
                padding: 8px 15px;
                min-width: 180px;
                font-size: 14px;
                font-weight: extra-bold;
            }}
            QComboBox:hover {{
                border-color: #808080;
            }}
            QComboBox::drop-down {{
                width: 30px;
                border-left: 1px solid #B0B0B0;
            }}
            QComboBox QAbstractItemView {{
                background-color: {combo_bg};
                color: {combo_text};
                selection-background-color: {button_bg};
                selection-color: white;
                border: 1px solid #B0B0B0;
            }}
        """)
        
        # Combo Actividad
        self.combo_actividad = QComboBox()
        self.combo_actividad.addItems(["leer",
                                       "relajarse",
                                       "conducir",
                                       "ejercicio",
                                       "socializar",
                                       "trabajar-estudiar",
                                       "dormir",
                                       "bailar",
                                       "fiesta",
                                       "pasear",
                                       "meditar",
                                       "cocinar-comer",
                                       "boda",
                                       "llorar",
                                       "cantar"])
        self.combo_actividad.setCurrentText("Actividad")
        self.combo_actividad.setStyleSheet(self.combo_emocion.styleSheet())
        
        # Botón Generar
        self.btn_generar = QPushButton(" Generar Playlist")
        self.btn_generar.setIcon(QIcon("media/generate_icon.svg"))
        self.btn_generar.setIconSize(QSize(20, 20))
        self.btn_generar.clicked.connect(self.generar_playlist)
        self.btn_generar.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_bg};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 160px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_pressed};
            }}
        """)
        
        # Añadir controles al layout
        controls_layout.addWidget(self.combo_emocion)
        controls_layout.addWidget(self.combo_actividad)
        controls_layout.addWidget(self.btn_generar)
        controls_layout.addStretch()
        
        layout.addWidget(controls_frame)
        
        # --- Área de resultados ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        
        # Placeholder
        placeholder = QLabel("Tus playlists generadas aparecerán aquí")
        placeholder.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14px;
                padding: 30px;
                text-align: center;
            }
        """)
        placeholder.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(placeholder)
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
        # --- Footer ---
        footer = QLabel("Playlist Generator | v0.2.3")
        footer.setStyleSheet("""
            QLabel {
                color: #707070;
                font-size: 11px;
                padding-top: 5px;
            }
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
    def cargar_dataset(self):
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Convertir a DataFrame
        # Normalizar nombres de columnaS
        df = pd.DataFrame(data['dataset'])
         # Normalizar los datos: convertir a minúsculas y quitar acentos
        df['emociones_relacionadas'] = df['emociones_relacionadas'].apply(
            lambda x: [unidecode.unidecode(e.strip().lower()) for e in x]
        )
        
        df['actividades_afines'] = df['actividades_afines'].apply(
            lambda x: [unidecode.unidecode(a.strip().lower()) for a in x] if isinstance(x, list) else []
        )

        return df
    
    def generar_playlist(self):
        # Limpiar resultados anteriores
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Convertir a minúsculas y eliminar espacios
        emocion = self.combo_emocion.currentText().strip().lower()
        actividad = self.combo_actividad.currentText().strip().lower()
        
        if emocion == "emoción" or actividad == "actividad":
            error_label = QLabel("Por favor, selecciona una emoción y una actividad válidas.")
            error_label.setStyleSheet("font: 12px; color: red;")
            error_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(error_label)
            return
                
        # Motor de inferencia
        motor = MotorInferencia()
        motor.reset()
        
        for _, row in self.df.iterrows():
            motor.declare(SongFact(
                artista_banda=row['artista/banda'],
                cancion=row['cancion'],
                emociones_relacionadas=row['emociones_relacionadas'],
                actividades_afines=row['actividades_afines'],
                youtube_link=row.get('youtube_link', ''),
                spotify_link=row.get('spotify_link', ''),
                genero=row.get('genero', '')
            ))
        
        motor.declare(UserSelections(
            emotion=emocion,
            activity=actividad
        ))
        
        motor.run()
        
        if motor.recomendaciones:
            # Seleccionar máximo 6 canciones aleatorias
            muestra_recomendaciones = random.sample(
                motor.recomendaciones, 
                min(6, len(motor.recomendaciones))
            )
  
            for cancion in muestra_recomendaciones: # Asumo que muestra_recomendaciones está definida
                # Frame para cada canción
                song_frame = QFrame()
                song_frame.setStyleSheet("""
                    QFrame {
                        background-color: #404040;
                        border: 1px solid #555555;
                        border-radius: 8px;
                    }
                """)
                song_frame.setMinimumHeight(270) # El song_frame tiene una altura mínima
                song_frame.setMaximumHeight(270) # El song_frame tiene una altura máxima
                
                frame_layout = QHBoxLayout(song_frame)
                frame_layout.setContentsMargins(10, 10, 20, 10)
                
                # --- Contenedor para la información de la canción ---
                info_widget = QWidget()
                info_widget.setFixedWidth(400)
                # Para que el centrado vertical funcione, info_widget necesita poder ocupar espacio vertical.
                # Si no se especifica, su política de tamaño vertical por defecto podría ser Preferred.
                # Si info_widget se expande verticalmente (ej. con QSizePolicy.Expanding), el centrado será más notable.
                # Vamos a asumir que info_widget tiene suficiente altura para que el centrado sea visible.

                info_layout = QVBoxLayout(info_widget)
                # No establecemos info_layout.setAlignment aquí para la alineación vertical del bloque,
                # ya que los stretches lo manejarán.
                info_layout.setContentsMargins(10, 0, 10, 0)
                info_layout.setSpacing(5)

                # --- Configurar los labels ---
                estilo_artista = """
                    QLabel {
                        color: #CCCCCC;
                        font: bold 20px 'Segoe UI';
                        qproperty-alignment: 'AlignCenter'; 
                        padding: 5px 5px 5px 5px; /* Añadido padding */
                    }
                """
                estilo_cancion = """
                    QLabel {
                        color: white;
                        font: bold 28px 'Segoe UI';
                        qproperty-alignment: 'AlignCenter'; 
                        margin-bottom: 8px;
                        margin-top: 8px;
                        padding: 5px 5px 5px 5px; /* Añadido padding */
                    }
                """
                estilo_genero = """
                    QLabel {
                        color: #CCCCCC;
                        font: 14px 'Segoe UI';
                        qproperty-alignment: 'AlignCenter';
                        padding: 5px 5px 5px 5px; /* Añadido padding */
                    }
                """

                artista_label = QLabel(cancion['artista'])
                artista_label.setStyleSheet(estilo_artista)
                artista_label.setWordWrap(True)

                cancion_label = QLabel(cancion['cancion'])
                cancion_label.setStyleSheet(estilo_cancion)
                cancion_label.setWordWrap(True)

                genero_label = QLabel(cancion['genero'])
                genero_label.setStyleSheet(estilo_genero)
                genero_label.setWordWrap(True)

                # --- Añadir espaciadores y labels para centrar verticalmente el grupo ---
                info_layout.addStretch(1) # Espaciador flexible arriba
                
                info_layout.addWidget(artista_label, 0, Qt.AlignHCenter)
                info_layout.addWidget(cancion_label, 0, Qt.AlignHCenter)
                info_layout.addWidget(genero_label, 0, Qt.AlignHCenter)
                
                info_layout.addStretch(1) # Espaciador flexible abajo

                # --- Widget de medios ---
                media_widget = VideoWidget( # Asumo que VideoWidget está definida
                    youtube_url=cancion['youtube'],
                    spotify_url=cancion['spotify']
                )
                media_widget.setMinimumSize(300, 250)
                media_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) 

                # --- Añadir info_widget y media_widget al frame_layout principal ---
                frame_layout.addWidget(info_widget)
                frame_layout.addWidget(media_widget)
                
                self.scroll_layout.addWidget(song_frame)
        else:
            no_results = QLabel("No se encontraron canciones que coincidan con tu selección")
            no_results.setStyleSheet("font: 12px; color: black;")
            no_results.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(no_results)
