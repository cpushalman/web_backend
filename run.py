# run.py
import os
from dotenv import load_dotenv
from core.main_app import MainApp
import sys

sys.path.append("C:/Users/Ahamed shalman/Documents/GitHub/preethicodes/web_backend")

load_dotenv()

main_app = MainApp()
app = main_app.get_app()

if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=int(os.environ.get('PORT')))


