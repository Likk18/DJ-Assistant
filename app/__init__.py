from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
