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
        self.setMinimumSize(80, 40)  # Tamaño ajustado para miniatura
        
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
        layout.addWidget(self.thumbnail_btn)

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
        
        self.spotify_btn = QPushButton("Abrir en Spotify")
        self.spotify_btn.clicked.connect(self.open_spotify)
        
        self.youtube_btn = QPushButton("Abrir en YouTube")
        self.youtube_btn.clicked.connect(self.open_youtube)
        
        btn_layout.addWidget(self.spotify_btn)
        btn_layout.addWidget(self.youtube_btn)
        layout.addLayout(btn_layout)

        # Estilo de los botones
        self.spotify_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font: bold 12px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #1ED760; }
        """)
        
        self.youtube_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font: bold 12px;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #CC0000; }
        """)

    def open_spotify(self):
        QDesktopServices.openUrl(QUrl(self.spotify_url))

    def open_youtube(self):
        QDesktopServices.openUrl(QUrl(self.youtube_url))

# Ejemplo de uso:
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QScrollArea
    
    app = QApplication(sys.argv)
    
    main_window = QMainWindow()
    main_widget = QWidget()
    main_layout = QGridLayout(main_widget)
    main_layout.setSpacing(15)
    
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(main_widget)
    
    main_window.setCentralWidget(scroll_area)
    main_window.setWindowTitle("Miniaturas de Videos")
    main_window.resize(800, 600)
    
    video_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"),
        ("https://youtu.be/9bZkp7q19f0", "https://open.spotify.com/track/03UrZgTINDqvnUMbbIMhql"),
        ("https://www.youtube.com/watch?v=kJQP7kiw5Fk", "https://open.spotify.com/track/6habFhsOp2NvshLv26DqMb"),
        ("https://youtu.be/JGwWNGJdvx8", "https://open.spotify.com/track/6RUKPb4LETWmmr3iAEQktW")
    ]
    
    for i, (yt_url, sp_url) in enumerate(video_urls):
        row = i // 2
        col = i % 2
        video_widget = VideoWidget(yt_url, sp_url)
        main_layout.addWidget(video_widget, row, col)
    
    main_window.show()
    sys.exit(app.exec_())