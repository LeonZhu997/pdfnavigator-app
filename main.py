"""PDFNavigator application entry point."""

import sys
from pathlib import Path
from PySide6.QtGui import QIcon

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PDFNavigator.ui.main_window import MainWindow


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("PDFNavigator")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("PDFNavigator")

    # Set application icon
    icon_path = Path(__file__).parent / "PDFNavigator" / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()