from PySide6.QtWidgets import QApplication
import sys
from .gui_factories import build_main_window
from .logging_setup import setup_logging



def main():
    app = QApplication(sys.argv)
    setup_logging()
    main_window = build_main_window()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())