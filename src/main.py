from flask import Flask, jsonify
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

# @app.before_request
# def create_tables():
#   db.drop_all()
#   db.create_all()
#   db.session.commit()


db = SQLAlchemy(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, DELETE, PUT'
    header['Access-Control-Allow-Headers'] = 'content-type, authorization'
    return response


@auth.verify_password
def verify_password(username, password):
    user1 = User.get_by_username(username)

    if user1 and User.check_hash(password, user1.password):
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

    @classmethod
    def delete(cls, myid):
        product = Product.get_by_id(myid)
        product_json = Product.save(product)
        product.query.filter_by(id=myid).delete()
        db.session.commit()
        return product_json


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('user', lazy='dynamic'))

    def save(self):
        return {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'password': self.password,
            'roles': [role.name for role in self.roles]
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
    def delete(cls, myid):
        user = User.get_by_id(myid)
        user_json = User.save(user)
        User.query.filter_by(id=myid).delete()
        db.session.commit()
        return user_json


@app.route("/api/v1/hello-world-29")
@handle_server_exception
@auth.login_required(role='admin')
def hello():
    return "Hello World 29"


@app.route("/product", methods=['POST'])
@handle_server_exception
def product():
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
        return {'message': 'Product name or description is already taken'}, 500


@app.route("/product", methods=['PUT'])
@handle_server_exception
def update_product():
    pars = reqparse.RequestParser()
    pars.add_argument('id', help='id cannot be blank', required=True)
    pars.add_argument('title', help='title cannot be blank', required=True)
    pars.add_argument('text', help='text cannot be blank', required=True)
    pars.add_argument('state', help='state cannot be blank', required=True)
    pars.add_argument('category', help='category cannot be blank', required=True)

    data = pars.parse_args()

    id = int(data['id'])

    try:
        product_1 = Product.query.filter_by(id=id).first()
        product_1.title = data['title']
        product_1.text = data['text']
        product_1.state = data['state']
        product_1.category = data['category']

        db.session.commit()
        return {'message': 'Product was successfully updated'}, 200
    except:
        return {'message': 'Product name or description is already taken'}, 500


@app.route('/product/<int:product_id>', methods=['GET'])
@handle_server_exception
@auth.login_required(role=['user', 'admin'])
def product_by_id(product_id):
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


@app.route('/product/all', methods=['GET'])
@handle_server_exception
def get_all_products():
    products = Product.query.all()
    serialized_products = [
        {
            'id': product.id,
            'title': product.title,
            'text': product.text,
            'state': product.state,
            'category': product.category
        }
        for product in products
    ]
    return jsonify({'products': serialized_products}), 200



@app.route('/product/<ProductId>', methods=['DELETE'])
@auth.login_required(role=['user', 'admin'])
@handle_server_exception
def delete_product_by_id(ProductId: int):
    username = auth.current_user()
    user = User.get_by_username(username)

    admin = Role.get_by_name('admin')
    if admin in user.roles:
        return Product.delete(ProductId)
    return Product.delete(ProductId)


@app.route('/user', methods=['POST'])
@handle_server_exception
def create_user():
    parser = reqparse.RequestParser()

    parser.add_argument('username', help='username cannot be blank', required=True)
    parser.add_argument('firstname', help='firstname cannot be blank', required=True)
    parser.add_argument('lastname', help='lastName cannot be blank', required=True)
    parser.add_argument('email', help='email cannot be blank', required=True)
    parser.add_argument('password', help='password cannot be blank', required=True)

    data = parser.parse_args()
    username = data['username']
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']
    password = data['password']
    password_hash = User.create_hash(password)

    if '@' not in email:
        return handle_error_format('Please, enter valid email address.', 'Field \'email\' in the request body.'), 400

    if len(password) < 8:
        return handle_error_format('Password should consist of at least 8 symbols.',
                                   'Field \'password\' in the request body.'), 400

    if User.get_by_username(username):
        return handle_error_format('User with such username already exists.',
                                   'Field \'username\' in the request body.'), 400

    user_1 = User(
        username=username,
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=password_hash
    )

    role = Role.get_by_name('user')
    user_1.roles.append(role)
    user_1.save_db()

    return {"message": "User was successfully created"}, 200


@app.route('/user/<userId>', methods=['PUT'])
@auth.login_required(role='admin')
@handle_server_exception
def update_user_by_id(userId: int):
    parser = reqparse.RequestParser()

    parser.add_argument('username', help='username cannot be blank')
    parser.add_argument('firstname', help='firstname cannot be blank')
    parser.add_argument('lastname', help='lastname cannot be blank')

    data = parser.parse_args()
    username = data['username']
    firstname = data['firstname']
    lastname = data['lastname']

    if User.get_by_username(username):
        return handle_error_format('User with such username already exists.',
                                   'Field \'username\' in the request body.'), 400

    user1 = User.get_by_id(userId)

    if not user1:
        return handle_error_format('User with such id does not exist.',
                                   'Field \'userId\' in path parameters.'), 404

    user1.username = username
    user1.firstname = firstname
    user1.lastname = lastname
    user1.save_db()

    return User.save(user1)


@app.route("/user/login", methods=["POST"])
@auth.login_required()
def login():
    return jsonify({"Success": "You are logged in successfully"})


@app.route("/user/logout", methods=["POST"])
def logout():
    return jsonify({"Success": "You successfully logged out"})


@app.route('/user/<userId>', methods=['DELETE'])
@auth.login_required(role='admin')
@handle_server_exception
def delete_user_by_id(userId: int):
    return User.delete(userId)


@app.route('/user/<string:username>', methods=['GET'])
@auth.login_required(role=['user', 'admin'])
def user_by_nickname3(username):
    user_1 = User.get_by_username(username)
    if not user_1:
        return handle_error_format('User with such username does not exist.',
                                   'Field \'username\' in the request body.'), 404

    return {
               "id": user_1.id,
               "username": user_1.username,
               "firstname": user_1.firstname,
               "lastname": user_1.lastname,
               "email": user_1.email,
               "password": user_1.password,
           }, 200


@app.route('/user/id/<userId>', methods=['GET'])
@auth.login_required(role='admin')
@handle_server_exception
def get_user_by_id(userId: int):
    user_1 = User.get_by_id(userId)
    if not user_1:
        return handle_error_format('User with such id does not exist.',
                                   'Field \'userId\' in path parameters.'), 404
    return {
               "id": user_1.id,
               "username": user_1.username,
               "firstname": user_1.firstname,
               "lastname": user_1.lastname,
               "email": user_1.email,
               "password": user_1.password,
           }, 200


if __name__ == "__main__":
    # serve(app)
    app.run(debug=True)
