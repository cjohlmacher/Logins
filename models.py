from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """ User model """

    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30),nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    @classmethod
    def register(cls,username,password,email,first_name,last_name):
        hashed_pwd = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed_pwd.decode('utf8')
        return cls(username=username,password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls,username,password):
        user = User.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.password,password):
                return user
        return None

    def __repr__(self):
        return f"<User {self.username} {self.email} {self.first_name} {self.last_name} Admin: {self.is_admin}>"

class Feedback(db.Model):
    """ Feedback model """

    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String,db.ForeignKey("users.username"))

    user = db.relationship('User', backref="feedback")

    def __repr__(self):
        return f"<Feedback {self.title} {self.content} by {self.username}>"