from flask import jsonify


class APIResponse:
    @staticmethod
    def construct_response(status, message, data=None, error=None):
        response = {
            'status': status,
            'message': message,
            'data': data,
            'error': error
        }
        return response

    @staticmethod
    def construct_error_response_and_close_session(code, message, session):
        session.close()
        error = {
            'code': code,
            'message': message,
        }

        return APIResponse.construct_response('error', 'Failed to process the request', error=error)

    @staticmethod
    def construct_error_response(code, message):
        error = {
            'code': code,
            'message': message,
        }

        return APIResponse.construct_response('error', 'Failed to process the request', error=error)
