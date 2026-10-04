from flask import Flask
from flask_login import LoginManager
from app.models.user import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-change-this-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:eastafrica2024@localhost:5432/humanitarian_data"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.auth import auth
    app.register_blueprint(auth)

    return app