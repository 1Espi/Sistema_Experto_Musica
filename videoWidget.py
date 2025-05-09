import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QApplication)
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QDesktopServices, QPixmap, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class VideoWidget(QWidget):
    def __init__(self, youtube_url, spotify_url, parent=None):
        super().__init__(parent)
        self.youtube_url = youtube_url
        self.spotify_url = spotify_url
        self.video_id = self.extract_video_id(youtube_url)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 5, 5, 2)
        layout.setAlignment(Qt.AlignTop)

        # Configurar miniatura
        self.setup_thumbnail(layout)
        
        # Botones de servicios
        self.setup_service_buttons(layout)

    def extract_video_id(self, url):
        patterns = [
            r'(?:v=|\/v\/|embed\/|shorts\/|watch\?.*v=)([\w-]{11})',
            r'youtu\.be\/([\w-]{11})'
        ]
        
        if not url:
            return None
            
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def setup_thumbnail(self, layout):
        # Contenedor para la miniatura
        self.thumbnail_btn = QPushButton()
        self.thumbnail_btn.setCursor(Qt.PointingHandCursor)
        self.thumbnail_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #444;
                border-radius: 4px;
                background: #333;
            }
            QPushButton:hover {
                border-color: #666;
            }
        """)
        self.thumbnail_btn.setFixedSize(320, 180)
        self.thumbnail_btn.clicked.connect(self.open_youtube)

        # Crear un layout horizontal contenedor para centrar
        container_layout = QHBoxLayout()
        container_layout.addStretch()  # Espacio flexible a la izquierda
        container_layout.addWidget(self.thumbnail_btn)
        container_layout.addStretch()  # Espacio flexible a la derecha

        # Añadir el layout contenedor al layout principal
        layout.addLayout(container_layout)

        # Cargar miniatura desde YouTube
        if self.video_id:
            self.load_thumbnail_image()
        else:
            self.show_thumbnail_error()

    def load_thumbnail_image(self):
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.handle_thumbnail_response)
        
        thumbnail_url = f"https://img.youtube.com/vi/{self.video_id}/0.jpg"
        request = QNetworkRequest(QUrl(thumbnail_url))
        self.network_manager.get(request)

    def handle_thumbnail_response(self, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            pixmap = pixmap.scaled(320, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            icon = QIcon(pixmap)
            self.thumbnail_btn.setIcon(icon)
            self.thumbnail_btn.setIconSize(pixmap.size())
        else:
            self.show_thumbnail_error()

    def show_thumbnail_error(self):
        self.thumbnail_btn.setText("Miniatura no disponible")
        self.thumbnail_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font: bold 12px;
                border: 2px solid #444;
            }
        """)

    def setup_service_buttons(self, layout):
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 0)
        
        # Crear botones con iconos
        self.spotify_btn = QPushButton()
        self.spotify_btn.clicked.connect(self.open_spotify)
        
        self.youtube_btn = QPushButton()
        self.youtube_btn.clicked.connect(self.open_youtube)
        
        # Cargar iconos SVG desde la carpeta media
        spotify_icon = QIcon("media/spotify_icon.svg")
        youtube_icon = QIcon("media/youtube_icon.svg")
        
        # Configurar iconos y texto
        self.spotify_btn.setText("Abrir en Spotify")
        self.spotify_btn.setIcon(spotify_icon)
        self.spotify_btn.setIconSize(QSize(24, 24))  # Tamaño del icono
        
        self.youtube_btn.setText("Abrir en YouTube")
        self.youtube_btn.setIcon(youtube_icon)
        self.youtube_btn.setIconSize(QSize(24, 24))  # Tamaño del icono
        
        btn_layout.addWidget(self.spotify_btn)
        btn_layout.addWidget(self.youtube_btn)
        layout.addLayout(btn_layout)

        # Estilo de los botones (actualizado para incluir iconos)
        self.spotify_btn.setStyleSheet("""
            QPushButton {
                background-color: #1ED760;
                color: white;
                border-radius: 4px;
                padding: 8px 12px 8px 8px;  /* Más padding a la izquierda para el icono */
                font: bold 12px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #1DB954; }
        """)
        
        self.youtube_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                border-radius: 4px;
                padding: 8px 12px 8px 8px;  /* Más padding a la izquierda para el icono */
                font: bold 12px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #CC0000; }
        """)
    
    def open_spotify(self):
        QDesktopServices.openUrl(QUrl(self.spotify_url))

    def open_youtube(self):
        QDesktopServices.openUrl(QUrl(self.youtube_url))
