import netifaces
from .qt import QtGui, QtCore, QtWidgets
import os
import sys

if sys.version_info < (3,):
    ustr = unicode
else:
    ustr = str


def get_subprocess_info():
    """
    Returns a tuple with the executable in which the ReReRemote server will be
    run and a list of arguments that should be prepended when called.
    """

    # Running in cx_freeze?
    if getattr(sys, 'frozen', False):
        # Return the server executable in the same path. No arguments needed.
        dirname = os.path.dirname(sys.executable)
        executable = os.path.join(dirname, 'rereremote')
        args = []

        # Windows? Add .exe suffix
        if os.name == 'nt':
            executable += '.exe'
    else:
        # Return the same Python interpreter, with the server package specified
        # as an argument.
        executable = sys.executable
        args = ['-m', 'rereremote.main']

    return executable, args


class ServerWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ServerWidget, self).__init__(parent)
        self.initGui()
        self.process = None

    def initGui(self):
        self.setWindowTitle("Re Re Remote")
        self.setWindowIcon(QtGui.QIcon(":/icon.png"))

        self.mainLayout = QtWidgets.QVBoxLayout(self)

        self.inputs = QtWidgets.QFormLayout()
        self.mainLayout.addLayout(self.inputs)

        self.txtPassword = QtWidgets.QLineEdit()
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.inputs.addRow("&Password", self.txtPassword)

        self.txtPasswordCheck = QtWidgets.QLineEdit()
        self.txtPasswordCheck.setEchoMode(QtWidgets.QLineEdit.Password)
        self.inputs.addRow("Password (&check, optional)", self.txtPasswordCheck)

        self.cmbInterfaces = self.initInterfaces()
        self.inputs.addRow("Listen on &interface", self.cmbInterfaces)

        self.txtPort = QtWidgets.QLineEdit()
        self.txtPort.setValidator(QtGui.QIntValidator(1025, 65535))
        self.txtPort.setText("1234")
        self.inputs.addRow("Listen on &port", self.txtPort)

        self.buttons = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.buttons)
        self.buttons.addStretch()
        buttonWidth = 80

        self.btnStart = QtWidgets.QPushButton("&Start")
        self.btnStart.setMinimumWidth(buttonWidth)
        self.btnStart.clicked.connect(self.start)
        self.btnStart.setDefault(True)
        self.buttons.addWidget(self.btnStart)

        self.btnStop = QtWidgets.QPushButton("St&op")
        self.btnStop.setMinimumWidth(buttonWidth)
        self.btnStop.clicked.connect(self.stop)
        self.buttons.addWidget(self.btnStop)

        self.buttons.addStretch()

        self.txtLog = QtWidgets.QTextEdit()
        self.txtLog.setReadOnly(True)
        self.mainLayout.addWidget(self.txtLog)

        self.setEnabledStates(False)
        self.center_on_screen()

    def start(self):
        password = self.txtPassword.text()
        password_check = self.txtPasswordCheck.text()
        address = self.cmbInterfaces.itemData(self.cmbInterfaces.currentIndex())
        port = self.txtPort.text()

        if password_check != "" and password != password_check:
            QtWidgets.QMessageBox.warning(self, "Passwords don't mach",
                  "You have provided a check password, but it does not match " +
                  "with the other password field.")
            self.txtPassword.setFocus()
            self.txtPassword.selectAll()
            return

        self.txtLog.clear()

        self.process = QtCore.QProcess(self)

        # Set password as an environment variable
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("REREREMOTE_KEY", password)
        self.process.setProcessEnvironment(env)

        self.process.readyReadStandardOutput.connect(self.readStdout)
        self.process.readyReadStandardError.connect(self.readStderr)
        self.process.finished.connect(self.processFinished)

        executable, args = get_subprocess_info()
        args += ['-a', address, '-p', port]
        self.process.start(executable, args)
        started = self.process.waitForStarted()

        if not started:
            QtWidgets.QMessageBox.warning(self, "Process failed",
                    "%s: %s" % 
                    (executable, self.process.errorString()))
        else:
            self.setEnabledStates(True)

    def writeToLog(self, text):
        self.txtLog.moveCursor(QtGui.QTextCursor.End)
        self.txtLog.insertPlainText(text)
        self.txtLog.moveCursor(QtGui.QTextCursor.End)

    def readStdout(self):
        output = self.process.readAllStandardOutput()
        self.writeToLog(ustr(output, 'UTF-8'))

    def readStderr(self):
        output = self.process.readAllStandardError()
        self.writeToLog(ustr(output, 'UTF-8'))
    
    def stop(self):
        if self.process:
            self.process.kill()
            self.process = None

    def processFinished(self, exitCode):
        self.writeToLog("\nServer has been stopped.")
        self.setEnabledStates(False)

    def setEnabledStates(self, serverRunning):
        self.txtPassword.setEnabled(not serverRunning)
        self.txtPasswordCheck.setEnabled(not serverRunning)
        self.cmbInterfaces.setEnabled(not serverRunning)
        self.txtPort.setEnabled(not serverRunning)
        
        self.btnStart.setEnabled(not serverRunning)
        self.btnStop.setEnabled(serverRunning)

    def initInterfaces(self):
        cmbInterfaces = QtWidgets.QComboBox()

        cmbInterfaces.addItem("Listen on all interfaces", "0.0.0.0")

        ifaces = netifaces.interfaces()
        for iface in ifaces:
            addresses = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
            for addrinfo in addresses:
                ip = addrinfo['addr']
                # Skip localhost, nobody wants to listen just there
                if ip == "127.0.0.1":
                    continue
                txt = "%s (%s)" % (iface, ip)
                cmbInterfaces.addItem(txt, ip)

        return cmbInterfaces

    def closeEvent(self, event):
        if self.process:
            self.stop()
            event.accept()

    def center_on_screen(self):
        mouse_pos = QtGui.QCursor.pos()
        screen_dimensions = QtWidgets.QDesktopWidget().screenGeometry(mouse_pos)

        self.move(screen_dimensions.center() - self.rect().center())
