from application import db

# User (Optional – for admin / instructor)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="admin")
    created_at = db.Column(db.DateTime, default=db.func.now())

    incexp = db.relationship('IncomeExpTracker', back_populates='user')

    def __repr__(self):
        return f"<User {self.email}>"
    
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    avatar_url = db.Column(db.String(20))

    user = db.relationship('User', backref='profile')

class IncomeExpTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id",  ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(50), default='Income', nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
   
    user = db.relationship('User', back_populates='incexp')
    