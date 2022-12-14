from unittest import TestCase, mock
from src.main import User, Product, product, update_product, product_by_id, create_user, \
    user_by_nickname3, update_user_by_id, delete_user_by_id, delete_product_by_id
from src.main import User, Role
from undecorated import undecorated
from src.main import verify_password, get_user_roles, hello, Role


class TestAuth(TestCase):

    def setUp(self) -> None:
        self.user = User(
            username='username',
            firstname='firstname',
            lastname='lastname',
            email='email',
            password='password'
        )

        self.user.roles.append(Role(id=1, name='user'))
        self.user.roles.append(Role(id=2, name='admin'))

    @mock.patch('src.main.User.check_hash')
    @mock.patch('src.main.User.get_by_username')
    def test_verify_password(self, mock_get_by_username, mock_check_hash):
        mock_get_by_username.return_value = self.user
        mock_check_hash.return_value = True

        undecorated_verify_password = undecorated(verify_password)
        result = undecorated_verify_password('username', 'password')

        self.assertEqual('username', result)

    @mock.patch('src.main.User.get_by_username')
    def test_get_user_roles(self, mock_get_by_username):
        mock_get_by_username.return_value = self.user

        undecorated_get_user_roles = undecorated(get_user_roles)
        result = undecorated_get_user_roles('username')

        self.assertEqual(['user', 'admin'], result)

    def test_hello(self):
        undecorated_hello = undecorated(hello)
        result = undecorated_hello()

        self.assertEqual(result, 'Hello World 29')


class TestRole(TestCase):

    def test_to_json(self):
        role = Role(id=1, name='user')
        expected_json = {'id': 1, 'name': 'user'}

        result = role.to_json()

        self.assertEqual(expected_json, result)

    @mock.patch('src.main.db.session.commit')
    @mock.patch('src.main.db.session.add')
    def test_save_to_db(self, mock_add, mock_commit):
        role = Role(id=1, name='user')

        mock_add.return_value = None
        mock_commit.return_value = None

        Role.save_to_db(role)

        mock_add.assert_called_once_with(role)
        mock_commit.assert_called_once_with()

    @mock.patch('flask_sqlalchemy.model._QueryProperty.__get__')
    def test_get_by_name(self, mock_query_property_getter):
        role = Role(id=1, name='user')
        mock_query_property_getter.return_value.filter_by.return_value.first.return_value = role

        result = Role.get_by_name('user')

        self.assertEqual(role, result)


class TestProduct(TestCase):

    def test_save(self):
        product = Product(id=1, title="plug", text="goody",
                          state="new", category="electronics")

        expected_json = {'id': 1, 'title': 'plug', 'text': 'goody',
                         'state': 'new', 'category': 'electronics'}

        result = product.save()

        self.assertEqual(expected_json, result)

    @mock.patch('src.main.db.session.commit')
    @mock.patch('src.main.db.session.add')
    def test_save_db(self, mock_add, mock_commit):
        product = Product(id=1, title="plug", text="goody",
                          state="new", category="electronics")

        mock_add.return_value = None
        mock_commit.return_value = None

        Product.save_db(product)

        mock_add.assert_called_once_with(product)
        mock_commit.assert_called_once_with()

    @mock.patch('flask_sqlalchemy.model._QueryProperty.__get__')
    def test_get_by_id(self, mock_query_property_getter):
        product = Product(id=1, title="plug", text="goody",
                          state="new", category="electronics")
        mock_query_property_getter.return_value.filter_by.return_value.first.return_value = product

        result = Product.get_by_id(1)

        self.assertEqual(product, result)

    @mock.patch('flask_sqlalchemy.model._QueryProperty.__get__')
    def test_get_by_title(self, mock_query_property_getter):
        product = Product(id=1, title="plug", text="goody",
                          state="new", category="electronics")
        mock_query_property_getter.return_value.filter_by.return_value.first.return_value = product

        result = Product.get_by_title("plug")

        self.assertEqual(product, result)

    @mock.patch('src.main.db.session.commit')
    @mock.patch('flask_sqlalchemy.model._QueryProperty.__get__')
    @mock.patch('src.main.Product.get_by_id')
    def test_delete(self, mock_get_by_id, mock_query_property_getter, mock_commit):
        product = Product(id=1, title="plug", text="goody",
                          state="new", category="electronics")
        mock_get_by_id.return_value = product
        mock_query_property_getter.return_value.filter_by.return_value.delete.return_value = None
        mock_commit.return_value = None

        result = Product.delete(1)

        self.assertEqual(product.save(), result)
        mock_get_by_id.assert_called_once_with(1)
        mock_query_property_getter.return_value.filter_by.assert_called_once_with(id=1)
        mock_query_property_getter.return_value.filter_by.return_value.delete.assert_called_once_with()
        mock_commit.assert_called_once_with()


class TestUser(TestCase):

    def setUp(self) -> None:
        self.user = User(
            username='username',
            firstname='firstname',
            lastname='lastname',
            email='email',
            password='password'
        )

    def test_save(self):
        user = self.user

        expected_json = {
            'email': 'email',
            'firstname': 'firstname',
            'id': None,
            'lastname': 'lastname',
            'password': 'password',
            'roles': [],
            'username': 'username'}

        result = user.save()

        self.assertEqual(expected_json, result)

    @mock.patch('src.main.db.session.commit')
    @mock.patch('src.main.db.session.add')
    def test_save_db(self, mock_add, mock_commit):
        user = self.user

        mock_add.return_value = None
        mock_commit.return_value = None

        User.save_db(user)

        mock_add.assert_called_once_with(user)
        mock_commit.assert_called_once_with()

    def test_create_hash(self):
        user = self.user

        result = user.create_hash('password')

        self.assertTrue(result)

    def test_check_hash(self):
        user = self.user
        user.password = user.create_hash('password')

        result = user.check_hash('password', user.password)

        self.assertTrue(result)

    @mock.patch('flask_sqlalchemy.model._QueryProperty.__get__')
    def test_get_by_id(self, mock_query_property_getter):
        user = self.user
        user.id = 1
        mock_query_property_getter.return_value.filter_by.return_value.first.return_value = user

        result = User.get_by_id(1)

        self.assertEqual(user, result)

    @mock.patch('flask_sqlalchemy.model._QueryProperty.__get__')
    def test_get_by_username(self, mock_query_property_getter):
        user = self.user
        mock_query_property_getter.return_value.filter_by.return_value.first.return_value = user

        result = User.get_by_username('username')

        self.assertEqual(user, result)

    @mock.patch('src.main.db.session.commit')
    @mock.patch('flask_sqlalchemy.model._QueryProperty.__get__')
    @mock.patch('src.main.User.get_by_id')
    def test_delete_2(self, mock_get_by_id, mock_query_property_getter, mock_commit):
        mock_get_by_id.return_value = self.user
        mock_query_property_getter.return_value.filter_by.return_value.delete.return_value = None
        mock_commit.return_value = None

        result = User.delete(1)

        self.assertEqual(result, User.save(self.user))


class TestProducts(TestCase):

    def setUp(self) -> None:
        self.product = Product(
            id=1,
            title='title',
            text='text',
            state='state',
            category='category'
        )

        self.product_json_create = {
            'id': 1,
            'title': 'Plug',
            'text': 'datext',
            'state': 'new',
            'category': 'electronics'
        }

        self.get_product_json = {
            'id': 1,
            'title': 'Plug',
            'text': 'datext',
            'state': 'new',
            'category': 'electronics'
        }

        self.update_product_json = {
            'id': 1,
            'title': 'new',
            'text': 'new',
            'state': 'new',
            'category': 'new'

        }

    @mock.patch('src.main.Product.save_db')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_product_create(self, mock_request_parser, mock_save_db):
        mock_request_parser.return_value = self.product_json_create
        mock_save_db.return_value = True
        undecorated_product = undecorated(product)
        result = undecorated_product()

        self.assertEqual(({'message': 'Product was successfully created'}, 200), result)

    @mock.patch('src.main.Product.save_db')
    @mock.patch('src.main.Product.save')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_update_product(self, mock_request_parser, mock_save_to_db, mock_save):
        mock_request_parser.return_value = self.update_product_json
        mock_save_to_db.return_value = True
        mock_save.return_value = Product.save(self.product)

        undecorated_update_product = undecorated(update_product)
        result = undecorated_update_product()

        self.get_product_json['username'], self.get_product_json['first_name'], self.get_product_json[
            'last_name'] = 'new', 'new', 'new'

        self.assertEqual(({'message': 'Product name or description is alredy taken'}, 500), result)

    @mock.patch('src.main.Product.get_by_id')
    def test_product_by_id(self, mock_product_by_id):
        mock_product_by_id.return_value = self.product

        undecorated_product_by_id = undecorated(product_by_id)
        result = undecorated_product_by_id(1)

        self.assertEqual(({'category': 'category',
                           'id': 1,
                           'state': 'state',
                           'text': 'text',
                           'title': 'title'},
                          200), result)

    @mock.patch('src.main.Product.get_by_id')
    def test_product_by_id_with_validation_error(self, mock_product_by_id):
        mock_product_by_id.return_value = None

        undecorated_product_by_id = undecorated(product_by_id)
        result = undecorated_product_by_id(1)

        self.assertEqual((
            {'errors': [{'message': 'Product with such id does not exist.',
                         'source': "Field 'Id' in path parameters."}],
             'traceId': result[0].get('traceId')}, 400), result)

    @mock.patch('src.main.Product.delete')
    @mock.patch('src.main.Product.get_by_id')
    @mock.patch('src.main.Role.get_by_name')
    @mock.patch('src.main.User.get_by_username')
    @mock.patch('flask_httpauth.HTTPAuth.current_user')
    def test_delete_product_by_id(self, mock_current_user, mock_get_by_username, mock_get_by_name, mock_get_by_id,
                                  mock_delete):
        mock_current_user.return_value = 'username'
        mock_get_by_id.return_value = self.product
        mock_delete.return_value = Product.save(self.product)

        undecorated_delete_account_by_id = undecorated(delete_product_by_id)
        result = undecorated_delete_account_by_id(1)

        self.assertEqual({'category': 'category',
                          'id': 1,
                          'state': 'state',
                          'text': 'text',
                          'title': 'title'}, result)


class TestUsers(TestCase):

    def setUp(self) -> None:
        self.user = User(
            username='username',
            firstname='firstname',
            lastname='lastname',
            email='email',
            password='password'
        )

        self.user_json_create = {
            'username': 'testmepls',
            'firstname': 'Yevhen',
            'lastname': 'Shcherbak',
            'email': 'mocke@gmail.com',
            'password': 'iexist23fd'
        }

        self.get_user_json = {
            'email': 'email',
            'firstname': 'firstname',
            'id': None,
            'lastname': 'lastname',
            'password': 'password',
            'roles': [],
            'username': 'username'
        }

        self.get_user_json_no_roles = {
            'email': 'email',
            'firstname': 'firstname',
            'id': None,
            'lastname': 'lastname',
            'password': 'password',
            'username': 'username'
        }

        self.update_user_json = {
            'username': 'new',
            'firstname': 'new',
            'lastname': 'new'
        }

    @mock.patch('src.main.User.save_db')
    @mock.patch('src.main.Role.get_by_name')
    @mock.patch('src.main.User.get_by_username')
    @mock.patch('src.main.User.create_hash')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_create_user(self, mock_request_parser, mock_create_hash, mock_get_by_username, mock_get_by_name,
                         mock_save_db):
        mock_request_parser.return_value = self.user_json_create
        mock_create_hash.return_value = 'password'
        mock_get_by_username.return_value = False
        mock_get_by_name.return_value = Role(id=1, name='user')
        mock_save_db.return_value = True

        result = create_user()

        self.assertEqual(({'message': 'User was successfully created'}, 200), result)

    @mock.patch('src.main.User.get_by_username')
    def test_user_by_username(self, mock_get_by_username):
        mock_get_by_username.return_value = self.user

        undecorated_get_by_username = undecorated(user_by_nickname3)
        result = undecorated_get_by_username(1)

        self.assertEqual((self.get_user_json_no_roles, 200), result)

    @mock.patch('src.main.User.get_by_username')
    def test_get_user_by_username_with_validation_error(self, mock_get_by_username):
        mock_get_by_username.return_value = None

        undecorated_get_by_username = undecorated(user_by_nickname3)
        result = undecorated_get_by_username(1)

        self.assertEqual(({'errors': [{'message': 'User with such username does not exist.',
                                       'source': "Field 'username' in the request body."}],
                           'traceId': result[0].get('traceId')}, 404), result)

    @mock.patch('src.main.User.create_hash')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_create_user_with_email_check_fail(self, mock_request_parser, mock_create_hash):
        self.user_json_create['email'] = 'invalid'

        mock_request_parser.return_value = self.user_json_create
        mock_create_hash.return_value = 'password'

        result = create_user()

        self.assertEqual(({'errors': [{'message': 'Please, enter valid email address.',
                                       'source': "Field 'email' in the request body."}],
                           'traceId': result[0].get('traceId')}, 400), result)

    @mock.patch('src.main.User.create_hash')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_create_user_with_password_check_fail(self, mock_request_parser, mock_create_hash):
        self.user_json_create['password'] = 'pass'

        mock_request_parser.return_value = self.user_json_create
        mock_create_hash.return_value = 'password'

        result = create_user()

        self.assertEqual(({'errors': [{'message': 'Password should consist of at least 8 symbols.',
                                       'source': "Field 'password' in the request body."}],
                           'traceId': result[0].get('traceId')}, 400), result)

    @mock.patch('src.main.User.get_by_username')
    @mock.patch('src.main.User.create_hash')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_create_user_with_username_check_fail(self, mock_request_parser, mock_create_hash, mock_get_by_username):
        mock_request_parser.return_value = self.user_json_create
        mock_create_hash.return_value = 'password'
        mock_get_by_username.return_value = True

        result = create_user()

        self.assertEqual(({'errors': [{'message': 'User with such username already exists.',
                                       'source': "Field 'username' in the request body."}],
                           'traceId': result[0].get('traceId')}, 400), result)

    @mock.patch('src.main.User.save_db')
    @mock.patch('src.main.User.get_by_id')
    @mock.patch('src.main.User.get_by_username')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_update_user_by_id(self, mock_request_parser, mock_get_by_username, mock_get_by_id, mock_save_db):
        mock_request_parser.return_value = self.update_user_json
        mock_get_by_username.return_value = None
        mock_get_by_id.return_value = self.user
        mock_save_db.return_value = True

        undecorated_update_user_by_id = undecorated(update_user_by_id)
        result = undecorated_update_user_by_id(1)

        self.get_user_json['username'], self.get_user_json['first_name'], self.get_user_json[
            'last_name'] = 'new', 'new', 'new'

        self.assertEqual({'email': 'email',
                          'firstname': 'new',
                          'id': None,
                          'lastname': 'new',
                          'password': 'password',
                          'roles': [],
                          'username': 'new'}, result)

    @mock.patch('src.main.User.get_by_username')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_update_user_by_id_with_invalid_id(self, mock_request_parser, mock_get_by_username):
        mock_request_parser.return_value = self.update_user_json
        mock_get_by_username.return_value = self.user

        undecorated_update_user_by_id = undecorated(update_user_by_id)
        result = undecorated_update_user_by_id(1)

        self.assertEqual(({'errors': [{'message': 'User with such username already exists.',
                                       'source': "Field 'username' in the request body."}],
                           'traceId': result[0].get('traceId')}, 400), result)

    @mock.patch('src.main.User.get_by_id')
    @mock.patch('src.main.User.get_by_username')
    @mock.patch('flask_restful.reqparse.RequestParser.parse_args')
    def test_update_user_by_id_with_invalid_username(self, mock_request_parser, mock_get_by_username, mock_get_by_id):
        mock_request_parser.return_value = self.update_user_json
        mock_get_by_username.return_value = None
        mock_get_by_id.return_value = None

        undecorated_update_user_by_id = undecorated(update_user_by_id)
        result = undecorated_update_user_by_id(1)

        self.assertEqual(({'errors': [{'message': 'User with such id does not exist.',
                                       'source': "Field 'userId' in path parameters."}],
                           'traceId': result[0].get('traceId')}, 404), result)

    @mock.patch('src.main.User.delete')
    def test_delete_user_by_id(self, mock_delete):
        mock_delete.return_value = self.get_user_json

        undecorated_delete_user_by_id = undecorated(delete_user_by_id)
        result = undecorated_delete_user_by_id(1)

        self.assertEqual(self.get_user_json, result)
