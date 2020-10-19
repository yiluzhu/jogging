from sqlalchemy.inspection import inspect
from sqlalchemy.util import symbol


class FieldNotFound(Exception):
    """Raises when the field of filter is missing"""


class Field:
    def __init__(self, model, field_name):
        self.model = model
        self.field_name = field_name

    def get_sqlalchemy_field(self):
        if self.field_name not in self.get_valid_field_names():
            raise FieldNotFound(
                'Model {} has no column `{}`.'.format(
                    self.model, self.field_name
                )
            )
        sqlalchemy_field = getattr(self.model, self.field_name)

        return sqlalchemy_field

    def get_valid_field_names(self):
        inspect_mapper = inspect(self.model)
        columns = inspect_mapper.columns
        orm_descriptors = inspect_mapper.all_orm_descriptors

        column_names = columns.keys()
        hybrid_names = [
            key for key, item in orm_descriptors.items()
            if is_hybrid_property(item) or is_hybrid_method(item)
        ]

        return set(column_names) | set(hybrid_names)


def is_hybrid_property(orm_descriptor):
    return orm_descriptor.extension_type == symbol('HYBRID_PROPERTY')


def is_hybrid_method(orm_descriptor):
    return orm_descriptor.extension_type == symbol('HYBRID_METHOD')


def get_query_model(query):
    """Get the model from query.

    :param query:
        A :class:`sqlalchemy.orm.Query` instance.

    :returns:
        A model.
    """
    return query.column_descriptions[0]['entity']
