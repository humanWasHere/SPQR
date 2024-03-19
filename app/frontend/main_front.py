# import sys
# from PySide2.QtWidgets import QGuiApplication, QMainWindow, QPushButton, QLabel, QFileDialog


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Select a file")
#         self.setGeometry(100, 100, 300, 200)
#         self.button = QPushButton("Browse", self)
#         self.button.setGeometry(100, 50, 100, 30)
#         self.button.clicked.connect(self.select_file)
#         self.label = QLabel("", self)
#         self.label.setGeometry(100, 100, 200, 30)

#     def select_file(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Select a file", "", "All files (*.*)")
#         if file_path:
#             self.label.setText(file_path)


# if __name__ == "__main__":
#     app = QGuiApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())
from PySide2 import QtCore, QtGui


class SoftwareEngineer:
    def __init__(self):
        self.app = QtGui.QGuiApplication([])
        self.button = QtGui.QPushButton("Test File")
        self.button.clicked.connect(self.do_file)
        self.button.show()
        self.fname = ""

    def do_file(self):
        self.fname = QtGui.QFileDialog.getOpenFileName()
        print(self.fname)

    def run(self):
        self.app.exec_()


# if __name__ == "__main__":
#     se = SoftwareEngineer()
#     se.run()
