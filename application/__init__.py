from flask import Flask, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os

# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cashflow.db'
# app.config['SECRET_KEY'] = '!@#$%^800965wqqeqeqqwqeqwew'

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cashflow.db'
    # app.config['SECRET_KEY'] = 'change_this_in_render'

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret")
    app.config['WTF_CSRF_ENABLED'] = True

    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    db.init_app(app)

    from application.routes import routes_bp
    app.register_blueprint(routes_bp)

    return app

# Decorator
def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please, login to continue', 'warning')
            return redirect(url_for('routes.sign_in'))
        return f(*args, **kwargs)
    return decorator

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get(role) != role:
                abort(404)
            return f(*args, **kwargs)
        return decorated
    return wrapper
from application import routes