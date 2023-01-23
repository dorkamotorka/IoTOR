from project import db
from project import ma

from marshmallow_sqlalchemy import auto_field
from marshmallow import fields, validate
from project import validators


class Node(db.Model):
    """Represents our Entry/Intermediate/Exit Node."""

    __tablename__ = "nodes"
    # autogenerated primary key
    id = db.Column(db.Integer, primary_key=True)

    # name/description of the node
    name = db.Column(db.String, unique=True)

    # type of the node (exit etc.)
    kind = db.Column(db.String)

    # address where the node is reachable, e.g. <hostname>:<port>
    address = db.Column(db.String, unique=True)

    # public key of the node
    public_key = db.Column(db.String, unique=True)

    def get_addr(self):
        return self.address

    def __str__(self):
        return f"Node[kind={self.kind},address={self.address},name={self.name}]"

class NodeSchema(ma.SQLAlchemySchema):
    """Schema (SQL and Validation) for Node"""

    class Meta:
        model = Node
        load_instance = True

    # expose those fields to REST API
    name = fields.Str(required=True, validate=validators.no_duplicate_node_names)
    kind = fields.Str(required=True, validate=validate.OneOf(["entry", "intermediate", "exit"]))
    address = fields.Str(required=True)
    public_key = auto_field(required=True)