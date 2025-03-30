from flask import Flask
from modules import app_APK, app_sub, app_pr,app_admin
import os

app = Flask(__name__)

# Register blueprints with error handling
try:
    app.register_blueprint(app_APK.app, url_prefix='/APK')
    app.register_blueprint(app_sub.app, url_prefix='/sub')
    app.register_blueprint(app_pr.app, url_prefix='/pr')
    app.register_blueprint(admin.app, url_prefix='/admin')
except Exception as e:
    print(f"Error registering blueprint: {e}")

if __name__ == '__main__':
    # Use environment variables for debug mode and port
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug_mode, port=port)
