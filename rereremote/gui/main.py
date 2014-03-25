import sys

# cx_freeze requires absolute imports in order to work
from rereremote.gui.qt import QtWidgets
from rereremote.gui.serverwidget import ServerWidget
from rereremote.gui.resources import resources_rc

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
