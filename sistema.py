import collections.abc
import sys

if sys.version_info >= (3, 10):
    sys.modules['collections'].Mapping = collections.abc.Mapping

from customtkinter import *
import pandas as pd
import json
from experta import *
from videoWidget import VideoWidget

# Definición de hechos para el sistema experto
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

class Sistema():
    def __init__(self):
        self.window = CTk()
        self.window.title("Sistema de recomendación musical")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        self.window.configure(fg_color="#2B2B2B")
        
        self.df = self.cargar_dataset()
        self.crear_interfaz()
        
    def cargar_dataset(self):
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data['dataset'])
        # Normalizar datos a minúsculas
        df['emociones_relacionadas'] = df['emociones_relacionadas'].apply(
            lambda x: [e.strip().lower() for e in x])
        df['actividades_afines'] = df['actividades_afines'].apply(
            lambda x: [a.strip().lower() for a in x])
        return df
    
    def crear_interfaz(self):
        self.emocion = CTkComboBox(self.window, values=["Nostalgia", 
                                                        "Tranquilidad", 
                                                        "Melancolia", 
                                                        "Confusion", 
                                                        "Deseo", 
                                                        "Euforia", 
                                                        "Energia", 
                                                        "Ansiedad", 
                                                        "Sarcasmo", 
                                                        "Alegria", 
                                                        "Euforia", 
                                                        "Esperanza", 
                                                        "Ternura", 
                                                        "Intimidad", 
                                                        "Misterio", 
                                                        "Instrospeccion", 
                                                        "Alienacion", 
                                                        "Vulnerabilidad", 
                                                        "Intensidad", 
                                                        "Tristeza", 
                                                        "Desamor", 
                                                        "Drama", 
                                                        "Extasis", 
                                                        "Proteccion", 
                                                        "Soledad", 
                                                        "Vulnerabilidad", 
                                                        "Resignacion", 
                                                        "Proteccion", 
                                                        "Calidez", 
                                                        "Devocion", 
                                                        "Paz",
                                                        "Optimismo",
                                                        "Introspeccion",
                                                        "Calma",
                                                        "Celos",
                                                        "Frustracion",
                                                        "Rebeldia",
                                                        "Minimalismo",
                                                        "Sospecha",
                                                        "Misterio",
                                                        "Arrepentimiento",
                                                        "Coqueteria",
                                                        "Diversion",
                                                        "Pasion",
                                                        "Ira",
                                                        "Ambivalencia",
                                                        "Desamor",
                                                        "Angustia",
                                                        "Satira",
                                                        "Determinacion",
                                                        "Empoderamiento",
                                                        "Gratitud",
                                                        "Heroismo",
                                                        "Curiosidad",
                                                        "Frustracion",
                                                        "Aceptacion",
                                                        "Rabia",
                                                        "Misticismo",
                                                        "Pasion",
                                                        "Comunidad",
                                                        "Remordimiento",
                                                        "Dolor",
                                                        "Union",
                                                        "Desconexion",
                                                        "Obsesion",
                                                        "Luto",
                                                        "Oscuridad",
                                                        "Romance",
                                                        "Sensualidad",
                                                        "Fascinacion",
                                                        "Furia",
                                                        "Felicidad",
                                                        "Atraccion",
                                                        "Relajacion",
                                                        "Hedonismo",
                                                        "Amistad",
                                                        "Despecho",
                                                        "Inocencia",
                                                        "Arrogancia",
                                                        "Desesperacion",
                                                        "Caos",
                                                        "Libertad",
                                                        "Superacion",
                                                        "Futurismo"])  # Valores originales
        self.emocion.pack(pady=20)
        self.emocion.set("Selecciona una emoción")
        
        self.actividad = CTkComboBox(self.window, values=["Leer", 
                                            "Relajarse", 
                                            "Conducir", 
                                            "Socializar", 
                                            "Escribir", 
                                            "Viajar", 
                                            "Bailar", 
                                            "Ejercicio", 
                                            "Nochear", 
                                            "Reflexionar", 
                                            "Fiestas",
                                            "Ejercicio",
                                            "Videojuegos",
                                            "Cantar",
                                            "Trabajar",
                                            "Llorar",
                                            "Pasear",
                                            "Abrazar",
                                            "Pintar",
                                            "Dormir",
                                            "Tocar Guitarra",
                                            "Cenar",
                                            "Yoga",
                                            "Meditar",
                                            "Activismo",
                                            "Correr",
                                            "Maquillarse",
                                            "Inspirarse",
                                            "Gritar",
                                            "Acampar",
                                            "Karaoke",
                                            "Dibujar",
                                            "Chatear",
                                            "Filosofar",
                                            "Picnic",
                                            "Citas",
                                            "Caminar",
                                            "Tomar",
                                            "Poesia",
                                            "Terapia",
                                            "Desayuno",
                                            "Comida",
                                            "Cena",
                                            "Cocinar",
                                            "Compras",
                                            "Desahogarse",
                                            "Bodas",
                                            ])  # Valores originales
        self.actividad.pack(pady=20)
        self.actividad.set("Selecciona una actividad")
        
        self.boton_crear = CTkButton(
            self.window, 
            text="Crear Playlist", 
            command=self.crear_playlist
        )
        self.boton_crear.pack(pady=20)
        
        self.resultados = CTkScrollableFrame(
            self.window,
            width=650,
            height=500,
            fg_color="#333333"
        )
        self.resultados.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Añadir label de título
        self.titulo_resultados = CTkLabel(
            self.window, 
            text="Recomendaciones Musicales",
            font=("Arial", 16, "bold")
        )
        self.titulo_resultados.pack(pady=5)
    
    def crear_playlist(self):
        emocion = self.emocion.get().strip().lower()
        actividad = self.actividad.get().strip().lower()
        
        # Limpiar resultados anteriores
        for widget in self.resultados.winfo_children():
            widget.destroy()
        
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
        
        # Mostrar resultados
        if motor.recomendaciones:
            for cancion in motor.recomendaciones:
                # Frame para cada canción
                song_frame = CTkFrame(
                    self.resultados,
                    fg_color="#404040",
                    border_width=1,
                    border_color="#555555",
                    corner_radius=8
                )
                song_frame.pack(fill="x", pady=5, padx=5)
                
                # Contenido izquierdo (info canción)
                info_frame = CTkFrame(song_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=10)
                
                CTkLabel(
                    info_frame,
                    text=f"{cancion['artista']}",
                    font=("Arial", 12, "bold"),
                    anchor="w"
                ).pack(fill="x")
                
                CTkLabel(
                    info_frame,
                    text=f"{cancion['cancion']}",
                    font=("Arial", 11),
                    text_color="#CCCCCC",
                    anchor="w"
                ).pack(fill="x")
                
                # Contenido derecho (botones y video)
                media_frame = CTkFrame(song_frame, fg_color="transparent")
                media_frame.pack(side="right", padx=10)
                
                VideoWidget(
                    media_frame,
                    youtube_url=cancion['youtube'],
                    spotify_url=cancion['spotify']
                ).pack(side="right")
                
        else:
            CTkLabel(
                self.resultados,
                text="No se encontraron canciones que coincidan con tu selección",
                font=("Arial", 12)
            ).pack(pady=20)
    
    def iniciar(self):
        self.window.mainloop()
