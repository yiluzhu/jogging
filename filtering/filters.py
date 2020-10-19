from collections import namedtuple
from collections.abc import Iterable
from inspect import signature
from itertools import chain

from sqlalchemy import and_, or_, not_

from filtering.models import Field, get_query_model


BooleanFunction = namedtuple(
    'BooleanFunction', ('key', 'sqlalchemy_fn', 'only_one_arg')
)
BOOLEAN_FUNCTIONS = [
    BooleanFunction('or', or_, False),
    BooleanFunction('and', and_, False),
    BooleanFunction('not', not_, True),
]


class BadFilterFormat(Exception):
    """Raises when the format of filter is wrong"""


class Operator:

    OPERATORS = {
        '==': lambda f, a: f == a,
        'eq': lambda f, a: f == a,
        '!=': lambda f, a: f != a,
        'ne': lambda f, a: f != a,
        '>': lambda f, a: f > a,
        'gt': lambda f, a: f > a,
        '<': lambda f, a: f < a,
        'lt': lambda f, a: f < a,
        '>=': lambda f, a: f >= a,
        'ge': lambda f, a: f >= a,
        '<=': lambda f, a: f <= a,
        'le': lambda f, a: f <= a,
        'in': lambda f, a: f.in_(a),
        'not_in': lambda f, a: ~f.in_(a),
    }

    def __init__(self, operator=None):
        if operator not in self.OPERATORS:
            raise BadFilterFormat('Operator `{}` not valid.'.format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)


class Filter:
    def __init__(self, filter_dict):
        self.filter_dict = filter_dict

        try:
            filter_dict['field']
        except KeyError:
            raise BadFilterFormat('`field` is a mandatory filter attribute.')
        except TypeError:
            raise BadFilterFormat(
                'Filter spec `{}` should be a dictionary.'.format(filter_dict)
            )

        self.operator = Operator(filter_dict.get('op'))
        self.value = filter_dict.get('value')
        value_present = True if 'value' in filter_dict else False
        if not value_present and self.operator.arity == 2:
            raise BadFilterFormat('`value` must be provided.')

    def get_named_models(self):
        if "model" in self.filter_dict:
            return {self.filter_dict['model']}
        return set()

    def format_for_sqlalchemy(self, query, default_model):
        operator = self.operator
        value = self.value

        model = get_query_model(query)

        function = operator.function
        arity = operator.arity

        field_name = self.filter_dict['field']
        field = Field(model, field_name)
        sqlalchemy_field = field.get_sqlalchemy_field()

        if arity == 1:
            return function(sqlalchemy_field)

        if arity == 2:
            return function(sqlalchemy_field, value)


class BooleanFilter:
    def __init__(self, function, *filters):
        self.function = function
        self.filters = filters

    def get_named_models(self):
        models = set()
        for filter in self.filters:
            models.update(filter.get_named_models())
        return models

    def format_for_sqlalchemy(self, query, default_model):
        return self.function(*[
            filter.format_for_sqlalchemy(query, default_model)
            for filter in self.filters
        ])


def is_iterable_filter(filter_dict):
    return isinstance(filter_dict, Iterable) and not isinstance(filter_dict, ((str, ), dict))


def build_filters(filter_dict):
    """ Recursively process `filter_dict` """

    if is_iterable_filter(filter_dict):
        return list(chain.from_iterable(
            build_filters(item) for item in filter_dict
        ))

    if isinstance(filter_dict, dict):
        # Check if filter spec defines a boolean function.
        for boolean_function in BOOLEAN_FUNCTIONS:
            if boolean_function.key in filter_dict:
                # The filter spec is for a boolean-function
                # Get the function argument definitions and validate
                fn_args = filter_dict[boolean_function.key]

                if not is_iterable_filter(fn_args):
                    raise BadFilterFormat(
                        '`{}` value must be an iterable across the function '
                        'arguments'.format(boolean_function.key)
                    )
                if boolean_function.only_one_arg and len(fn_args) != 1:
                    raise BadFilterFormat(
                        '`{}` must have one argument'.format(
                            boolean_function.key
                        )
                    )
                if not boolean_function.only_one_arg and len(fn_args) < 1:
                    raise BadFilterFormat(
                        '`{}` must have one or more arguments'.format(
                            boolean_function.key
                        )
                    )
                return [
                    BooleanFilter(
                        boolean_function.sqlalchemy_fn, *build_filters(fn_args)
                    )
                ]

    return [Filter(filter_dict)]


def apply_filters(query, filter_dict):
    """Apply filters to a SQLAlchemy query.

    :param query:
        A :class:`sqlalchemy.orm.Query` instance.

    :param filter_dict:
        A dict or an iterable of dicts, where each one includes
        the necesary information to create a filter to be applied to the
        query.

    :returns:
        The :class:`sqlalchemy.orm.Query` instance after all the filters
        have been applied.
    """
    if not filter_dict:
        return query

    filters = build_filters(filter_dict)
    model = get_query_model(query)
    sqlalchemy_filters = [filter.format_for_sqlalchemy(query, model) for filter in filters]
    if sqlalchemy_filters:
        query = query.filter(*sqlalchemy_filters)

    return query
