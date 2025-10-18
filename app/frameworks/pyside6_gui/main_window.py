from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar, QMenu, QInputDialog, QFileDialog
from PySide6.QtGui import QAction
from typing import Optional

from app.interface_adapters.gui.presenters.main_window_presenter import MainWindowPresenter
from app.interface_adapters.gui.controllers.main_window_controller import MainWindowController
from app.interface_adapters.gui.views.main_window_view import MainWindowView


class MainWindow(QMainWindow):
    def __init__(self, 
                 presenter: MainWindowPresenter, 
                 controller: MainWindowController, 
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._presenter = presenter
        self._controller = controller
        
        self._presenter.attach_view(self)
        self._init_elements()
    
    
    def _init_elements(self):
        self._init_menu_bar()
        
    
    def _init_menu_bar(self):
        menu_bar = QMenuBar(self)
        
        main_menu = QMenu(parent=menu_bar, title="File")
        
        new_project_action = QAction(parent=main_menu, text="New Project")
        new_project_action.triggered.connect(self._controller.on_new_project_triggered)
        save_project_action = QAction(parent=main_menu, text="Save")
        save_project_action.triggered.connect(self._controller.on_save_project_triggered)
        load_project_action = QAction(parent=main_menu, text="Load")
        load_project_action.triggered.connect(self._controller.on_load_project_triggered)
        
        main_menu.addActions([
            new_project_action,
            save_project_action,
            load_project_action
        ])
        
        menu_bar.addMenu(main_menu)
        
        self.setMenuBar(menu_bar)
    
    
    def prompt_project_name(self) -> Optional[str]:
        text, ok = QInputDialog.getText(self, "New Project", "Project name:")
        return text if ok else None
        
    
    def prompt_location_for_new_project(self) -> Optional[str]:
        location = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select a folder",
            dir="../"
        )
        return location or None
    
    
    def prompt_existing_project_location(self) -> Optional[str]:
        location, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select project file",
            dir="../"
        )
        return location or None
