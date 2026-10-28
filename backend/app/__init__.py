from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config
from .models import db

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please log in to access this page.'

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    from .routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
    
    return app
