import json
from fernet_fields import EncryptedTextField


class EncryptedJSONField(EncryptedTextField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    def to_python(self, value):
        if value is None or isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value)
