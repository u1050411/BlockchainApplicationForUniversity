from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class LoginWeb(UserMixin):

    def __init__(self, id, password, tipus=False):
        self.id = id
        self.password = generate_password_hash(password)
        self.tipus = tipus

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)