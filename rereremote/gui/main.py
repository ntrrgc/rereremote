import sys
from .qt import QtCore, QtGui
from .serverwidget import ServerWidget
from .resources import resources_rc


def main():
    qapp = QtGui.QApplication(sys.argv)

    window = ServerWidget()
    window.show()

    qapp.exec_()


if __name__ == "__main__":
    main()
