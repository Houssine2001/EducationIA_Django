"""
Custom JSONField compatible with older SQLite versions
"""
import json
from django.db import models
from django.core.exceptions import ValidationError


class CompatibleJSONField(models.TextField):
    """
    JSONField compatible avec Python 3.7 et SQLite ancien
    Stocke les données JSON sous forme de texte
    """
    description = "JSON data stored as text"

    def __init__(self, *args, **kwargs):
        self.default_value = kwargs.pop('default', dict)
        if callable(self.default_value):
            kwargs['default'] = self.default_value
        else:
            kwargs['default'] = lambda: self.default_value
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            # Si c'est déjà une chaîne, vérifier si c'est du JSON valide
            try:
                json.loads(value)
                return value
            except:
                pass
        return json.dumps(value, ensure_ascii=False)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value is not None and not isinstance(value, (dict, list, str)):
            raise ValidationError(
                "%(field)s must be a dict, list, or valid JSON string",
                code='invalid',
                params={'field': self.name},
            )
