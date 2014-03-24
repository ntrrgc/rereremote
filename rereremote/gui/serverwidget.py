import netifaces
from .qt import QtGui, QtCore
import sys

if sys.version_info < (3,):
    ustr = unicode
else:
    ustr = str


class ServerWidget(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ServerWidget, self).__init__(parent)
        self.initGui()
        self.process = None

    def initGui(self):
        self.setWindowTitle("Re Re Remote")
        self.setWindowIcon(QtGui.QIcon(":/icon.png"))

        self.mainLayout = QtGui.QVBoxLayout(self)

        self.inputs = QtGui.QFormLayout()
        self.mainLayout.addLayout(self.inputs)

        self.txtPassword = QtGui.QLineEdit()
        self.txtPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.inputs.addRow("&Password", self.txtPassword)

        self.txtPasswordCheck = QtGui.QLineEdit()
        self.txtPasswordCheck.setEchoMode(QtGui.QLineEdit.Password)
        self.inputs.addRow("Password (&check, optional)", self.txtPasswordCheck)

        self.cmbInterfaces = self.initInterfaces()
        self.inputs.addRow("Listen on &interface", self.cmbInterfaces)

        self.txtPort = QtGui.QLineEdit()
        self.txtPort.setValidator(QtGui.QIntValidator(1025, 65535))
        self.txtPort.setText("1234")
        self.inputs.addRow("Listen on &port", self.txtPort)

        self.buttons = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.buttons)
        self.buttons.addStretch()
        buttonWidth = 80

        self.btnStart = QtGui.QPushButton("&Start")
        self.btnStart.setMinimumWidth(buttonWidth)
        self.btnStart.clicked.connect(self.start)
        self.btnStart.setDefault(True)
        self.buttons.addWidget(self.btnStart)

        self.btnStop = QtGui.QPushButton("St&op")
        self.btnStop.setMinimumWidth(buttonWidth)
        self.btnStop.clicked.connect(self.stop)
        self.buttons.addWidget(self.btnStop)

        self.buttons.addStretch()

        self.txtLog = QtGui.QTextEdit()
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
            QtGui.QMessageBox.warning(self, "Passwords don't mach",
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

        args = ['-u', '-m', 'rereremote.main',
                '-a', address.toString(),
                '-p', port]
        self.process.start(sys.executable, args)
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

    def processFinished(self, exitCode, exitStatus):
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
        cmbInterfaces = QtGui.QComboBox()

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
        screen_dimensions = QtGui.QDesktopWidget().screenGeometry(mouse_pos)

        self.move(screen_dimensions.center() - self.rect().center())
