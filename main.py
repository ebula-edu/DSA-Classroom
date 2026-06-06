import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    # Set high-DPI scaling configuration for high-resolution monitors
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        sys.modules.get("PySide6").QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Fusion style looks modern and uniform across Windows/Linux/Mac
    
    # Initialize main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
