from flask import Flask
from waitress import serve
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import reqparse
from flask import Flask, request
from passlib.hash import pbkdf2_sha256
from flask_httpauth import HTTPBasicAuth
from src.error_handler.exception_wrapper import handle_error_format
from src.error_handler.exception_wrapper import handle_server_exception

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:fojdb67332#@localhost:3306/shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False





db = SQLAlchemy(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()

@app.before_request
def create_tables():
 #db.drop_all()
 db.create_all()
 db.session.commit()


@auth.verify_password
def verify_password(username, password):
    user1 = User.get_by_username(username)

    if user1 and User.check_hash(password, user1.password_hash):
        return username


@auth.get_user_roles
def get_user_roles(user1):
    user_entity = User.get_by_username(user1)
    return [role.name for role in user_entity.roles]


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


class UsersRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    text = db.Column(db.String(50), unique=True, nullable=False)
    state = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def save(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'state': self.state,
            'category': self.category,
        }

    def save_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, myid):
        return Product.query.filter_by(id=myid).first()

    @classmethod
    def get_by_title(cls, mytitle):
        return Product.query.filter_by(title=mytitle).first()

    # дороби ерори
    @classmethod
    def delete(cls, myid):
        product = Product.get_by_id(myid)
        product_json = product.save(product)
        product.query.filter_by(id=myid).delete()
        db.session.commit()
        return product_json


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('user', lazy='dynamic'))

    def save(self):
        return {
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
    def delete(cls, myid):  # дороби ерори
        try:
            user = User.get_by_id(myid)
            user_json = User.save(user)
            User.query.filter_by(id=myid).delete()
            db.session.commit()
            return user_json
        except Exception:
            return


@app.route("/api/v1/hello-world-29")
@handle_server_exception
@auth.login_required(role='admin')
def hello():
    return "Hello World 29"


@app.route("/product", methods=['POST', 'PUT'])
@handle_server_exception
@auth.login_required(role='admin')
def product():
    if request.method == 'POST':  # +
        pars = reqparse.RequestParser()
        pars.add_argument('title', help='name cannot be blank', required=True)
        pars.add_argument('text', help='name cannot be blank', required=True)
        pars.add_argument('state', help='status cannot be blank', required=True)
        pars.add_argument('category', help='status cannot be blank', required=True)

        data = pars.parse_args()

        title = data['title']
        text = data['text']
        state = data['state']
        category = data['category']

        product_1 = Product(
            title=title,
            text=text,
            state=state,
            category=category
        )
        try:
            product_1.save_db()
            return {'message': 'Product was successfully created'}, 200
        except:
            return {'message': 'Product name or description is alredy taken'}, 500


    elif request.method == 'PUT':  # +
        pars = reqparse.RequestParser()
        pars.add_argument('id', help='id cannot be blank', required=True)
        pars.add_argument('title', help='title cannot be blank', required=True)
        pars.add_argument('text', help='text cannot be blank', required=True)
        pars.add_argument('state', help='state cannot be blank', required=True)
        pars.add_argument('category', help='category cannot be blank', required=True)

        data = pars.parse_args()
        id = int(data['id'])

        if not id:
            return handle_error_format('Product with such id does not exist.',
                                       'Field \'Id\' in path parameters.'), 400

        try:
            product_1 = Product.query.filter_by(id=id).first()
            print(Product.save(product_1))
            product_1.title = data['title']
            product_1.text = data['text']
            product_1.state = data['state']
            product_1.category = data['category']

            db.session.commit()
            return {'message': 'Product was successfully updated'}, 200
        except:
            return {'message': 'Product name or description is alredy taken'}, 500


@app.route('/product/<int:product_id>', methods=['GET'])
@handle_server_exception
@auth.login_required(role='user')
def product_by_id(product_id):
    try:
        product_1 = Product.get_by_id(product_id)

        if not product_1:
            return handle_error_format('Product with such id does not exist.',
                                       'Field \'Id\' in path parameters.'), 400

        return {'id': product_1.id,
                'title': product_1.title,
                'text': product_1.text,
                'state': product_1.state,
                'category': product_1.category
                }, 200
    except Exception:
        return {'message': 'Error'}, 500


@app.route('/product/<int:product_id>', methods=['DELETE'])
@handle_server_exception
@auth.login_required(role='admin')
def product_by_id2(product_id):
    if Product.query.filter_by(id=product_id).first() == None:
        return {"message": f"Product not found"}, 404
    try:
        Product.query.filter_by(id=product_id).delete()
        db.session.commit()
        return {"message": f"item is deleted"}, 200
    except Exception:
        return {"message": f"Something went wrong"}, 500


@app.route('/user', methods=['POST'])
@handle_server_exception
def create_user():
    pars = reqparse.RequestParser()
    pars.add_argument('username', help='username cannot be blank', required=True)
    pars.add_argument('firstname', help='firstName cannot be blank', required=True)
    pars.add_argument('lastname', help='lastName cannot be blank', required=True)
    pars.add_argument('email', help='email cannot be blank', required=True)
    pars.add_argument('password_hash', help='password cannot be blank', required=True)

    data = pars.parse_args()
    data['password_hash'] = User.create_hash(data['password_hash'])

    try:
        username = (data['username'])
        firstname = (data['firstname'])
        lastname = data['lastname']
        email = data['email']
        password_hash = data['password_hash']
    except Exception:
        return {'message': 'error'}, 500

    user_1 = User(
        username=username,
        firstname=firstname,
        lastname=lastname,
        email=email,
        password_hash=password_hash
    )
    if '@' not in email:
        return handle_error_format('Please, enter valid email address.', 'Field \'email\' in the request body.'), 400

    if User.get_by_username(username):
        return handle_error_format('User with such username already exists.',
                                   'Field \'username\' in the request body.'), 400

    try:
        role = Role.get_by_name("user")
        user_1.roles.append(role)
        user_1.save_db()
        return {"message": "User was successfully created"}, 200
    except Exception:
        return {"message": "Username Or Email are alredy taken"}, 500


@app.route('/user/<string:username>', methods=['PUT', 'DELETE'])
#@handle_server_exception
@auth.login_required(role='user')
def user_by_nickname(username):
    username1 = auth.current_user()
    userr = User.get_by_username(username1)
    admin = Role.get_by_name("admin")
    if username1 == username or admin in userr.roles:

        if request.method == 'PUT':  # +
            pars = reqparse.RequestParser()
            pars.add_argument('username', help='username cannot be blank', required=True)
            pars.add_argument('firstname', help='firstName cannot be blank', required=True)
            pars.add_argument('lastname', help='lastName cannot be blank', required=True)
            pars.add_argument('email', help='email cannot be blank', required=True)
            pars.add_argument('password_hash', help='password cannot be blank', required=True)

            data = pars.parse_args()
            data['password_hash'] = User.create_hash(data['password_hash'])

            try:
                User.query.filter_by(username=username).update(data)
                db.session.commit()
                return {"message": f"User {username} is updated"}
            except Exception:
                return {"message": "You haven't made any changes"}, 500

        elif request.method == 'DELETE':  # +
            try:
                temp = int(username)
                return {"message": "Bad request"}, 500
            except Exception:
                pass

            if User.query.filter_by(username=username).first() == None:
                return {"message": "User does not exist"}, 404

            try:
                User.query.filter_by(username=username).delete()
                db.session.commit()
                return {"message": f"user{username} was deleted"}, 200
            except Exception:
                return {"message": "Something went wrong"}, 500

    else:
        return {"message": "No permission"}, 401


@app.route('/user/<string:username>', methods=['GET'])
@auth.login_required(role='user')
def user_by_nickname3(username):
    user_1 = User.get_by_username(username)
    if not user_1:
        return handle_error_format('User with such username does not exist.',
                                   'Field \'username\' in the request body.'), 400

    return {
               "id": user_1.id,
               "username": user_1.username,
               "firstname": user_1.firstname,
               "lastname": user_1.lastname,
               "email": user_1.email,
               "password": user_1.password_hash,
           }, 200


if __name__ == "__main__":
    # serve(app)
    app.run(debug=True)
