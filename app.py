import datetime

from loguru import logger
from flask import Flask
from flask.json import JSONEncoder

from api.admin import admin_bp
from api.user import user_bp
from api.jogging import jogging_bp


def create_app():
    app = Flask(__name__)
    logger.add(
        'logs/log_{time:YYYY-MM-DD}.log',
        level='INFO',
        backtrace=True,
        rotation="1 week",
        retention="1 month"
    )
    # configure_hook(app)
    app.json_encoder = CustomJSONEncoder

    for bp in [admin_bp, user_bp, jogging_bp]:
        app.register_blueprint(bp)

    return app


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return str(obj)

        return super().default(obj)


# def configure_hook(app):
#
#     @app.before_request
#     def before_request():
#         if request.host.startswith(('localhost', '127.0.0.1')):
#             # Ignore authorization when running locally
#             return
#         if request.base_url.endswith(('/login')):
#             # Ignore authorization for these API
#             return
#
#         if request.method != 'OPTIONS':
#             auth_key = request.headers.get('Authorization')
#             if auth_key != AUTH_KEY:
#                 return Response('Unauthorized', 401)


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
