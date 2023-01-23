from application import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host=app.config['BIND_HOST'], port=app.config['PORT'], debug=False)
