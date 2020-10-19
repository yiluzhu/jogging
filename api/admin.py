from flask import request, jsonify, Blueprint
from loguru import logger
from services.db import dbs
from services.exceptions import UnauthenticatedError


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/heartbeat')
def heartbeat():
    return 'OK'


@admin_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username:
        return jsonify(status=1, msg='No username provided'), 400
    if not password:
        return jsonify(status=1, msg='No password provided'), 400

    try:
        token = dbs.login(username, password)
        logger.info(f'login token: {token}')
        return jsonify(status=0, msg='OK', token=token)

    except UnauthenticatedError as e:
        return jsonify(status=1, msg='Wrong username or password'), 401

    except Exception as e:
        return jsonify(status=1, msg=f'Failed to login: {e}'), 500

    finally:
        dbs.session.rollback()


@admin_bp.route('/logout')
def logout():
    token = request.headers.get('Authorization')
    logger.info('logout token:{}', token)

    try:
        dbs.logout(token)
        return jsonify(status=0, msg='OK')

    except Exception as e:
        msg = f'Error when logout with token {token}: {e}'
        logger.error(msg)
        return jsonify(status=2, msg=msg), 500

    finally:
        dbs.session.rollback()
