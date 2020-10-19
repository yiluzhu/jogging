import traceback
from flask import Blueprint, request, jsonify
from loguru import logger

from services.db import dbs
from services.config import DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NUM
from services import exceptions
from filtering.conversion import convert_str_to_filters


user_bp = Blueprint('user', __name__)


@user_bp.route('/user', methods=['PUT', 'POST'])
def create_or_update_user():
    token = request.headers.get('Authorization')

    try:
        if request.method == 'PUT':
            dbs.create_a_user(request.json, token)
        else:
            dbs.update_a_user(request.json, token)
        return jsonify(status=0, msg='OK')

    except exceptions.UnknownUser as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 409

    except exceptions.MissingInformation as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 409

    except exceptions.DuplicateUser as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 409

    except exceptions.UnauthenticatedError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 401

    except exceptions.NoAccessError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 403

    except Exception as e:
        traceback.print_exc()
        logger.error(f'{request.method} request failed: {e}')
        return jsonify(status=1, msg=f'Error: {e}'), 500

    finally:
        dbs.session.rollback()


@user_bp.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    token = request.headers.get('Authorization')

    try:
        dbs.delete_a_user(username, token)
        return jsonify(status=0, msg='OK')

    except exceptions.UnknownUser as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 409

    except exceptions.UnauthenticatedError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 401

    except exceptions.NoAccessError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 403

    except exceptions.UserStillHasRecords as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 409

    except Exception as e:
        traceback.print_exc()
        logger.error(f'{request.method} request failed: {e}')
        return jsonify(status=1, msg=f'Error: {e}'), 500
    finally:
        dbs.session.rollback()


@user_bp.route('/user')
def read_user_info():
    try:
        page = int(request.args.get('page', DEFAULT_PAGE_NUM))
        page_size = int(request.args.get('pagesize', DEFAULT_PAGE_SIZE))

    except Exception as e:
        return jsonify(status=1, msg=f'Invalid page or pagesize: {e}'), 400

    try:
        filter_str = request.args.get('filter')
        filters = convert_str_to_filters(filter_str)

    except Exception as e:
        traceback.print_exc()
        return jsonify(status=1, msg=f'Invalid filter {filter_str}: {e}'), 400

    token = request.headers.get('Authorization')

    try:
        logger.debug(f'Token: {token}. Filters for string {filter_str}: {filters}')
        data = dbs.read_user_info(token, filters, page, page_size)
        return jsonify(status=0, msg='OK', data=data)

    except exceptions.UnauthenticatedError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 401

    except exceptions.NoAccessError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 403

    except Exception as e:
        traceback.print_exc()
        logger.error(f'Failed to read user information: {e}')
        return jsonify(status=1, msg=f'ERROR: {e}'), 500

    finally:
        dbs.session.rollback()
