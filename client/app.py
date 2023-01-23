from project import create_app
import os

app = create_app()
app.secret_key = os.urandom(12).hex()
