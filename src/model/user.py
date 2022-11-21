from src.main import db
from passlib.hash import pbkdf2_sha256


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(50), nullable=False)


    def save(self):
        return{
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'password_hash': self.password_hash
        }

    def save_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def create_hash(password):
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def check_hash(password, myhash):
        return pbkdf2_sha256.verify(password, myhash)

    @classmethod
    def get_by_id(cls, myid):
        return User.query.filter_by(id=myid).first()

    @classmethod
    def get_by_username(cls, myusername):
        return User.query.filter_by(username=myusername).first()

    @classmethod
    def user_list(cls):
        def to_json(user):
            return {
             'id': user.id,
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'password_hash': user.password_hash
        }
        return {"users": [to_json(user) for user in User.query.all()]}

    @classmethod
    def delete(cls, myid):  #дороби ерори
        try:
            user=User.get_by_id(myid)
            user_json=User.save(user)
            User.query.filter_by(id=myid).delete()
            db.session.commit()
            return user_json
        except Exception:
            return