from django.db.models import DateField, FloatField, IntegerField, Model


class Move(Model):
    date = DateField(null=False)
    kind = IntegerField(null=False)
    quantity = FloatField(null=False)

    class Meta:
        db_table = "moves"
