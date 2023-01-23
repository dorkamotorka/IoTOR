# custom marshmallow validators

from marshmallow import ValidationError
from project import models

def no_duplicate_node_names(name: str):
    """
    implements unique=True constraint of Node.name
    """

    if models.Node.query.filter(models.Node.name == name).first() is not None:
        raise ValidationError(f"Value '{name}' already exists.")
