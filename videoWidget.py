from customtkinter import *
import webbrowser
import requests
from PIL import Image
import re

class VideoWidget(CTkFrame):
    def __init__(self, master, youtube_url, spotify_url, **kwargs):
        super().__init__(master, **kwargs)
        self.youtube_url = youtube_url
        self.spotify_url = spotify_url
        self.video_id = self.extract_video_id()
        
        self.configure(fg_color="transparent")
        self.create_widgets()
    
    def extract_video_id(self):
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, self.youtube_url)
        return match.group(1) if match else None
    
    def create_widgets(self):
        try:
            # Thumbnail interactivo
            thumbnail_url = f"https://img.youtube.com/vi/{self.video_id}/maxresdefault.jpg"
            response = requests.get(thumbnail_url, stream=True)
            image = Image.open(response.raw)
            image = image.resize((320, 180), Image.LANCZOS)
            
            self.tk_image = CTkImage(light_image=image, size=(320, 180))
            
            # Botón de thumbnail
            self.thumbnail_btn = CTkButton(
                self,
                image=self.tk_image,
                text="",
                fg_color="transparent",
                hover_color="#4A4A4A",
                command=self.open_youtube
            )
            self.thumbnail_btn.pack(pady=5)
            
            # Botones de control
            control_frame = CTkFrame(self, fg_color="transparent")
            control_frame.pack(pady=5)
            
            CTkButton(
                control_frame,
                text="Ver en YouTube",
                fg_color="#FF0000",
                hover_color="#CC0000",
                command=self.open_youtube
            ).pack(side="left", padx=5)
            
            CTkButton(
                control_frame,
                text="Abrir en Spotify",
                fg_color="#1DB954",
                hover_color="#1ED760",
                command=self.open_spotify
            ).pack(side="left", padx=5)
            
        except Exception as e:
            CTkLabel(self, text="Video no disponible").pack()
    
    def open_youtube(self):
        webbrowser.open(self.youtube_url)
    
    def open_spotify(self):
        webbrowser.open(self.spotify_url)