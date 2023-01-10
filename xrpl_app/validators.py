from django.core.exceptions import ValidationError


def validate_numeric(val: str):
    try:
        float(val)
    except Exception:
        raise ValidationError("Expected numeric string, but got invalid format "
                              "instead")
