import uuid
from sys import exc_info as stack_trace


def handle_server_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            return {
                       'traceId': str(uuid.uuid1()),
                       'errors': [str(error) for error in stack_trace()]
                   }, 500

    wrapper.__name__ = func.__name__
    return wrapper


def handle_error_format(message: str, source: str):
    return {
        'traceId': str(uuid.uuid1()),
        'errors': [
            {
                'message': message,
                'source': source
            }
        ]
    }
