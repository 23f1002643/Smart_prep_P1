from datetime import timedelta
# Configuration settings
config_settings = {
    'FLASK_DEBUG': True,
    'FLASK_APP': 'app.py',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite3',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'my_secret_key',
    'PERMANENT_SESSION_LIFETIME': timedelta(minutes=30)
}
