import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from interface import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./media/musical_note.ico"))  # Cambia "icon.png" por la ruta de tu icono
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
    
#para la base de conocimiento
# {
#       "artista/banda": ,
#       "cancion": ,
#       "genero": ,
#       "emociones_relacionadas": [],
#       "actividades_afines": [],
#       "youtube_link": "",
#       "spotify_link": ""
#     },