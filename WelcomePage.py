import sys
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog,QVBoxLayout
from courriers import CourriersWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        self.cour_window = None  # Initialize cour_window as None

    def init_ui(self):
        loadUi("mainpage.ui", self)
        self.bcour.clicked.connect(self.load_another_code)

    def load_another_code(self):
        # Hide the main window
        self.hide()
        # Load the UI file for cour
        self.cour_window = QDialog()
        loadUi("cour.ui", self.cour_window)
        self.cour_window.show()
        # Create an instance of CourriersWidget
        courriers_widget = CourriersWidget()
        # Check if the courriers_widget is not None before adding it to the layout
        if courriers_widget is not None:
            layout = QVBoxLayout()
            layout.addWidget(courriers_widget)  # Add the CourriersWidget to the layout
            self.cour_window.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
