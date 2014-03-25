import sys
from .qt import QtWidgets
from .serverwidget import ServerWidget
from .resources import resources_rc

# PyQt5 may crash if qApp goes out of scope, so make it global
qApp = None

def main():
    global qApp
    qApp = QtWidgets.QApplication(sys.argv)

    window = ServerWidget()
    window.show()

    qApp.exec_()

if __name__ == "__main__":
    main()
