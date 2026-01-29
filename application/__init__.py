from flask import Flask, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_migrate import Migrate

# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cashflow.db'
# app.config['SECRET_KEY'] = '!@#$%^800965wqqeqeqqwqeqwew'
mail = Mail()
db = SQLAlchemy()
migrate = Migrate()

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cashflow.db'
    # app.config['SECRET_KEY'] = 'change_this_in_render'

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret")
    app.config['WTF_CSRF_ENABLED'] = True

     # Folder to store uploaded images
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'smartcoder234@gmail.com'
    app.config['MAIL_PASSWORD'] = 'Ezekiel!@#$1'
    app.config['MAIL_DEFAULT_SENDER'] = 'CashFlow Tracker <smartcoder234@gmail.com>'

   
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    

    from application.routes import routes_bp
    from application.inc_routes.routes import inc_bp
    
    app.register_blueprint(routes_bp)
    app.register_blueprint(inc_bp)

    return app

def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and ext in ALLOWED_EXTENSIONS

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