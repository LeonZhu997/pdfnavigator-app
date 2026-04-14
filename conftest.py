# Root conftest.py - loaded before all plugins
# Patch Qt imports to prevent DLL loading errors

import sys


class DummyQtModule:
    """Dummy module to prevent Qt import errors."""
    def __getattr__(self, name):
        # Return callable functions or attributes as needed
        if name in ('qVersion', '__version__', 'PYQT_VERSION_STR', 'QT_VERSION_STR'):
            return lambda: "0.0.0"  # Callable that returns a version string
        if name.startswith('__') and name.endswith('__'):
            return getattr(type(self), name, None)
        return DummyQtModule()

    def __call__(self, *args, **kwargs):
        return DummyQtModule()


# Patch ALL Qt modules before any plugin tries to import them
qt_modules = [
    "QtCore", "QtWidgets", "QtGui", "QtNetwork", "QtXml", "QtSvg",
    "QtTest", "QtPrintSupport", "QtSql", "QtMultimedia", "QtMultimediaWidgets",
    "QtOpenGL", "QtOpenGLWidgets", "QtQuick", "QtQml", "QtQuickWidgets",
    "QtWebEngine", "QtWebEngineCore", "QtWebEngineWidgets", "QtWebChannel",
    "QtWebSockets", "QtBluetooth", "QtNfc", "QtPositioning", "QtLocation",
    "QtSensors", "QtSerialPort", "QtHelp", "QtDesigner", "QtUiTools",
    "QtAxContainer", "QtDBus", "QtPdf", "QtPdfWidgets"
]

# Pre-patch all Qt submodules in sys.modules
dummy = DummyQtModule()
for module_name in qt_modules:
    full_name = f"PySide6.{module_name}"
    sys.modules[full_name] = dummy

# Also ensure PySide6 package itself exists and has these as attributes
import PySide6
for module_name in qt_modules:
    if not hasattr(PySide6, module_name):
        setattr(PySide6, module_name, dummy)