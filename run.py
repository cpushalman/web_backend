# run.py

from core.main_app import MainApp



if __name__ == "__main__":
    main_app = MainApp()
    app = main_app.get_app()
    app.run(debug=True)    
