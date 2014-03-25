from __future__ import print_function

import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
sip.setapi('QStringList', 2)

import sys
import os
qt_package = os.environ.get('PY_QT_PACKAGE', 'guess')

if qt_package == "guess":
    packages = ('PyQt5', 'PyQt4', 'PySide')
    for package_name in packages:
        try:
            __import__(package_name)
            qt_package = package_name
            break
        except ImportError:
            pass
    else:
        print("Please install PyQt4, PyQt5 or PySide.", file=sys.stderr)
        sys.exit(1)

if qt_package == 'PyQt5':
    from PyQt5 import QtGui, QtCore, QtWidgets
elif qt_package == 'PyQt4':
    from PyQt4 import QtGui, QtCore
    QtWidgets = QtGui
elif qt_package == 'PySide':
    # PySide does not support Qt5
    from PySide import QtGui, QtCore
    QtWidgets = QtGui
else:
    print("PY_QT_PACKAGE environment variable has an invalid value: %s" % 
          qt_package, file=sys.stderr)
    print("Allowed values are: PyQt5, PyQt4, PySide, guess.", file=sys.stderr)
    sys.exit(1)
