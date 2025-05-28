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
    port = int(os.getenv("PORT", 8000))
    app.run(debug=True)


    
