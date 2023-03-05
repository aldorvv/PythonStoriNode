from uuid import uuid4

from django.db.models import FileField, ManyToManyField, Model
from django.forms import ValidationError

from ..moves.models import Move


def _validate_file_extension(req):
    if req.content_type != "text/csv":
        raise ValidationError("Please upload a .csv file.")


def _get_new_name(*args, **kwargs):
    return f"{uuid4()}.csv"


class Account(Model):
    file = FileField(
        null=False,
        validators=(_validate_file_extension,),
        unique=True,
        upload_to=_get_new_name,
    )
    moves = ManyToManyField(Move)

    class Meta:
        db_table = "accounts"
