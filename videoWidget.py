from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSlider)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtCore import QUrl, Qt, pyqtSlot
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import re

# Clase interceptora para bloquear solicitudes publicitarias
class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        
        # Bloquear solicitudes a dominios publicitarios
        if "googleads" in url or "doubleclick" in url:
            info.block(True)

class VideoWidget(QWidget):
    def __init__(self, youtube_url, spotify_url, parent=None):
        super().__init__(parent)
        self.youtube_url = youtube_url
        self.spotify_url = spotify_url
        
        layout = QVBoxLayout(self)
        
        # Extraer ID del video con regex
        video_id = None
        if youtube_url:
            # Busca patrones como v=ID, youtu.be/ID, o embed/ID
            match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', youtube_url)
            if match:
                video_id = match.group(1)
        
        if video_id:
            self.web_view = QWebEngineView()
            
            # Configurar el bloqueador de anuncios
            self.ad_blocker = AdBlocker()
            self.web_view.page().profile().setUrlRequestInterceptor(self.ad_blocker)
            
            # Agregar parámetros para control del reproductor
            embed_url = (
                f"https://www.youtube.com/embed/{video_id}?"
                "enablejsapi=1&"
                "origin=http://localhost&"
                "rel=0&"
                "modestbranding=1&"
                "controls=1&"
                "disablekb=1&"
                "fs=0&"
                "iv_load_policy=3"
            )
            
            self.web_view.load(QUrl(embed_url))
            self.web_view.setFixedSize(330, 170)
            
            # Inyectar CSS después de cargar
            self.web_view.loadFinished.connect(self.inject_css)
            layout.addWidget(self.web_view)
            
        else:
            error_label = QLabel("Enlace de YouTube no válido")
            layout.addWidget(error_label)
            
        btn_layout = QHBoxLayout()
        
        self.spotify_btn = QPushButton("Abrir en Spotify")
        self.spotify_btn.clicked.connect(self.open_spotify)
        btn_layout.addWidget(self.spotify_btn)
        
        self.youtube_btn = QPushButton("Abrir en YouTube")
        self.youtube_btn.clicked.connect(self.open_youtube)
        btn_layout.addWidget(self.youtube_btn)
        
        layout.addLayout(btn_layout)
    
        self.spotify_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
        """)
        
        self.youtube_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #CC0000;
            }
        """)
        
    def open_spotify(self):
        QDesktopServices.openUrl(QUrl(self.spotify_url))
    
    def open_youtube(self):
        QDesktopServices.openUrl(QUrl(self.youtube_url))
        
    def inject_css(self):
        # Crea un script que se inyectará en cada frame
        script = QWebEngineScript()
        script.setSourceCode("""
            document.addEventListener('DOMContentLoaded', function() {
                var style = document.createElement('style');
                style.type = 'text/css';
                style.textContent = `
                    .ytp-pause-overlay,
                    .ytp-watermark,
                    .ytp-chrome-top-buttons {
                        display: none !important;
                    }
                `;
                document.head.appendChild(style);
                
                // Capturar y suprimir errores de consola relacionados con CORS
                const originalFetch = window.fetch;
                window.fetch = function() {
                    return originalFetch.apply(this, arguments)
                        .catch(error => {
                            if (error.toString().includes('CORS')) {
                                // Suprimir error CORS
                                return new Response();
                            }
                            throw error;
                        });
                };
            });
        """)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setWorldId(QWebEngineScript.MainWorld)
        self.web_view.page().scripts().insert(script)