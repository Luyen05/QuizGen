"""Navigation helper."""


class NavigationManager:
    def __init__(self, app):
        self.app = app

    def show(self, name: str):
        self.app.show_screen(name)
