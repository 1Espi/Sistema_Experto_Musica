import sys
import collections.abc

if sys.version_info >= (3, 10):
    sys.modules['collections'].Mapping = collections.abc.Mapping

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
                             QScrollArea, QFrame, QLabel)
from PyQt5.QtCore import Qt
from experta import *
from videoWidget import VideoWidget
import pandas as pd
import json
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
import random
import unidecode

class AdBlockerInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        if "doubleclick.net" in info.requestUrl().host():
            info.block(True)

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
            cancion=MATCH.cancion
        ),
        TEST(lambda emotion, emociones: emotion in emociones),
        TEST(lambda activity, actividades: activity in actividades)
    )
    def agregar_recomendacion(self, artista, cancion, youtube, spotify):
        self.recomendaciones.append({
            "artista": artista,
            "cancion": cancion,
            "youtube": youtube,
            "spotify": spotify
        })

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Generador de Playlists")
        self.resize(800, 600)
        
        self.genero_seleccionado = ""
        self.estilo_seleccionado = ""
        self.recomendaciones = []  # Aquí irían las recomendaciones reales
        
        self.df = self.cargar_dataset()
        
        interceptor = AdBlockerInterceptor()
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controles superiores
        controls_layout = QHBoxLayout()
        
        self.combo_emocion = QComboBox()
        self.combo_emocion.addItems(["alegria",
                                     "tristeza",
                                     "euforia",
                                     "relajacion",
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
        controls_layout.addWidget(self.combo_emocion)
        
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
                                       "cocinar",
                                       "boda",
                                       "llorar",
                                       "cantar",
                                       "deportes"])
        controls_layout.addWidget(self.combo_actividad)
        
        self.btn_generar = QPushButton("Generar Playlist")
        self.btn_generar.clicked.connect(self.generar_playlist)
        controls_layout.addWidget(self.btn_generar)
        
        layout.addLayout(controls_layout)
        
        # Área de resultados con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        
        layout.addWidget(self.scroll_area)
        
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
            lambda x: [unidecode.unidecode(a.strip().lower()) for a in x]
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
                
        # Motor de inferencia
        motor = MotorInferencia()
        motor.reset()
        
        for _, row in self.df.iterrows():
            motor.declare(SongFact(
                artista_banda=row['artista/banda'],
                cancion=row['canción'],
                emociones_relacionadas=row['emociones_relacionadas'],
                actividades_afines=row['actividades_afines'],
                youtube_link=row.get('youtube_link', ''),
                spotify_link=row.get('spotify_link', '')
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
  
            for cancion in muestra_recomendaciones:
                # Frame para cada canción
                song_frame = QFrame()
                song_frame.setStyleSheet("""
                    QFrame {
                        background-color: #404040;
                        border: 1px solid #555555;
                        border-radius: 8px;
                    }
                """)
                song_frame.setMinimumHeight(160)
                
                frame_layout = QHBoxLayout(song_frame)
                frame_layout.setContentsMargins(10, 10, 10, 10)
                
                # Información de la canción
                info_layout = QVBoxLayout()
                info_layout.setAlignment(Qt.AlignTop)
                
                artista_label = QLabel(cancion['artista'])
                artista_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        font: bold 12px;
                    }
                """)
                info_layout.addWidget(artista_label)
                
                cancion_label = QLabel(cancion['cancion'])
                cancion_label.setStyleSheet("""
                    QLabel {
                        color: #CCCCCC;
                        font: 11px;
                    }
                """)
                info_layout.addWidget(cancion_label)
                
                frame_layout.addLayout(info_layout, 1)
                
                # Widget de medios
                media_widget = VideoWidget(
                    youtube_url=cancion['youtube'],
                    spotify_url=cancion['spotify']
                )
                frame_layout.addWidget(media_widget)
                
                self.scroll_layout.addWidget(song_frame)
        else:
            no_results = QLabel("No se encontraron canciones que coincidan con tu selección")
            no_results.setStyleSheet("font: 12px; color: white;")
            self.scroll_layout.addWidget(no_results)
