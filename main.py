"""PDFNavigator application entry point."""

import sys
from pathlib import Path
from PySide6.QtGui import QIcon

# Handle PyInstaller bundled path
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS) / relative_path
    else:
        # Running in development
        return Path(__file__).parent / relative_path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from pdfnavigator.ui.main_window import MainWindow


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("PDFNavigator")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("PDFNavigator")

    # Set application icon
    icon_path = get_resource_path("assets/icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()