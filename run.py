from application import db, create_app
from itsdangerous import URLSafeTimedSerializer
# from flask_migrate import Migrate


app = create_app()
# migrate = Migrate(app, db)

def generate_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt="email-confirm")

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.loads(token, salt="email-confirm", max_age=expiration)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    # app.run