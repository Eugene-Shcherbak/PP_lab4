from unittest import TestCase
from src.error_handler.exception_wrapper import handle_error_format
from src.error_handler.exception_wrapper import handle_server_exception


class TestUtils(TestCase):

    def func(self):
        return {'message': 'blank'}

    def test_handle_server_exception(self):
        result = handle_server_exception(self.func)
        self.assertNotEqual(result, {})

    def test_handle_error_format(self):
        result = handle_error_format('message', 'source')
        expected = {
            'traceId': result.get('traceId'),
            'errors': [
                {
                    'message': 'message',
                    'source': 'source'
                }
            ]
        }
        self.assertEqual(result, expected)