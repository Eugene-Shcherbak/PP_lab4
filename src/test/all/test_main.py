from unittest import TestCase, mock
from src.main import User, Product
from src.main import User, Role
from undecorated import undecorated
from src.main import verify_password, get_user_roles, hello, Role


class TestAuth(TestCase):

    def setUp(self) -> None:
        self.user = User(
            username='username',
            firstname='first_name',
            lastname='last_name',
            email='email',
            password_hash='password_hash'
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
