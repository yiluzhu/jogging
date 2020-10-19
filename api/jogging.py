import datetime
import traceback
from loguru import logger
from flask import Blueprint, request, jsonify

from services.db import dbs
from services.config import DEFAULT_PAGE_NUM, DEFAULT_PAGE_SIZE
from services import exceptions
from filtering.conversion import convert_str_to_filters


jogging_bp = Blueprint('jogging', __name__)


@jogging_bp.route('/record', methods=['PUT', 'POST'])
def create_or_update_record():
    token = request.headers.get('Authorization')
    try:
        if request.method == 'PUT':
            dbs.create_a_record(request.json, token)
        else:
            dbs.update_a_record(request.json, token)
        return jsonify(status=0, msg='OK')

    except exceptions.UnknownUser as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 409

    except exceptions.UnknownRecord as e:
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


@jogging_bp.route('/record/<rid>', methods=['DELETE'])
def delete_a_record(rid):
    token = request.headers.get('Authorization')
    try:
        rid = int(rid)

    except Exception as e:
        msg = f'Invalid record id: {rid}'
        logger.error(msg)
        return jsonify(status=1, msg=msg), 400

    try:
        dbs.delete_a_record(rid, token)
        return jsonify(status=0, msg='OK')

    except exceptions.UnknownRecord as e:
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


@jogging_bp.route('/record')
def read_records():
    try:
        page = int(request.args.get('page', DEFAULT_PAGE_NUM))
        page_size = int(request.args.get('pagesize', DEFAULT_PAGE_SIZE))

    except Exception as e:
        return jsonify(
            status=1, msg=f'Invalid page or pagesize: {e}'), 400

    try:
        filter_str = request.args.get('filter')
        filters = convert_str_to_filters(filter_str)

    except Exception as e:
        traceback.print_exc()
        return jsonify(status=1, msg=f'Invalid filter {filter_str}: {e}'), 400

    token = request.headers.get('Authorization')

    try:
        logger.debug(f'Page {page}, page size: {page_size}, token {token}, filters {filters}')
        data = dbs.read_records(token, filters, page, page_size)
        return jsonify(status=0, msg='OK', data=data)

    except exceptions.UnauthenticatedError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 401

    except exceptions.NoAccessError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 403

    except Exception as e:
        traceback.print_exc()
        logger.error(f'Failed to read jogging records: {e}')
        return jsonify(status=1, msg=f'ERROR: {e}'), 500

    finally:
        dbs.session.rollback()


@jogging_bp.route('/report')
def make_weekly_report():
    token = request.headers.get('Authorization')
    week_start_date = request.args.get('week_start_date')
    if week_start_date:
        week_start_date = datetime.datetime.strptime(week_start_date, '%Y-%m-%d').date()
    else:
        week_start_date = datetime.datetime.today() - datetime.timedelta(days=6)

    try:
        data = dbs.make_weekly_report(token, week_start_date)
        return jsonify(status=0, msg='OK', data=data)

    except exceptions.UnauthenticatedError as e:
        return jsonify(status=1, msg=f'ERROR: {e}'), 401

    except Exception as e:
        traceback.print_exc()
        logger.error(f'Failed to read jogging records: {e}')
        return jsonify(status=1, msg=f'ERROR: {e}'), 500

    finally:
        dbs.session.rollback()
