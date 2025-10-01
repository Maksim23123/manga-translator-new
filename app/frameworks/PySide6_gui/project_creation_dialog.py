from PySide6.QtWidgets import QDialog, QWidget
from typing import Optional



class ProjectCreationDialog(QDialog):
    
    def __init__(self, parent: Optional[QWidget]=None):
        super().__init__(parent = parent)
        self.setWindowTitle("Create Project")
        self.setBaseSize(300, 200)
        
        
    