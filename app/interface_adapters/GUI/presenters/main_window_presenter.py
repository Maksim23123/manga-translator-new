from typing import Optional

from ..views.main_window_view import MainWindowView



class MainWindowPresenter:
    
    view: Optional[MainWindowView] = None
    
    
    def attach_view(self, view: MainWindowView):
        self.view = view
    
    
    def request_project_name(self) -> Optional[str]:
        return self.view.prompt_project_name() if self.view else None