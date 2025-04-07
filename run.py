# run.py

from core.main_app import MainApp

app = MainApp().get_app()

if __name__ == '__main__':
    app.run(debug=True)
