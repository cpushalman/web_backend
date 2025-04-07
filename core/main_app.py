

from flask import Flask
from modules.app_bs import BSModule
from modules.app_admin import AdminModule
from modules.app_analytics import AnalyticsModule
from modules.app_shorten import ShortenModule

class MainApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.register_modules()

    def register_modules(self):
        self.app.register_blueprint(BSModule().get_blueprint())
        self.app.register_blueprint(AdminModule().get_blueprint())
        self.app.register_blueprint(AnalyticsModule().get_blueprint())
        self.app.register_blueprint(ShortenModule().get_blueprint())

    def get_app(self):
        return self.app
