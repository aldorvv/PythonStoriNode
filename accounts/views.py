import calendar
import csv
import json
from datetime import datetime as dt

from django.db.models import Avg, Sum
from django.forms import ValidationError
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from moves.models import Move
from utils import MediaStorage
from utils.mail import Email

from .models import Account
from .serializers import AccountSerializer

STORAGE = MediaStorage()


def _parse_date(str_date, fmt="%m/%d"):
    date_ = dt.strptime(str_date, fmt).replace(year=dt.today().year)
    return date_


def _parse_transaction(str_transaction):
    qty = float(str_transaction)
    kind = 1 if qty >= 0 else -1
    return qty, kind


def _parse_file(content):
    moves = []
    reader = csv.DictReader(content)
    for row in reader:
        date_ = _parse_date(row["Date"])
        qty, kind = _parse_transaction(row["Transaction"])
        data = {"quantity": qty, "kind": kind, "date": date_}
        moves.append(Move.objects.create(**data))
    return moves


def _get_monthly_counts(transactions):
    monthly_counts = []

    for i in range(1, 13):
        if count := transactions.filter(date__month=i).count():
            monthly_counts.append(
                {"count": count, "month": calendar.month_name[i]}
            )
    return monthly_counts


def _format_agg(result, name, attr="quantity", digits=2):
    return round(result[f"{attr}__{name}"], digits)


class AccountView(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def create(self, request, *args, **kwargs):
        file = self.request.FILES["file"]

        rows = _parse_file(file.read().decode().splitlines())
        instance = self.queryset.create(file=file)

        for move in rows:
            instance.moves.add(move)

        serializer = self.serializer_class(instance=instance)

        return HttpResponse(
            json.dumps(serializer.data),
            status=200,
            headers={"Content-Type": "application/json"},
        )

    @action(detail=True)
    def summary(self, request, *args, **kwargs):
        # Processing request info
        instance = self.get_object()
        recipient = request.query_params.get("email")
        if recipient is None:
            raise ValidationError(
                "Please specify an email to send the summary"
            )

        # Get info for summary
        moves = Move.objects.filter(account=instance)
        avg_deb = moves.filter(kind=-1).aggregate(Avg("quantity"))
        avg_cred = moves.filter(kind=1).aggregate(Avg("quantity"))
        total = moves.aggregate(Sum("quantity"))

        # Write and send email
        mail = Email("Your summary is here! 🚀")
        mail.compose(
            "summary.html",
            {
                "total": _format_agg(total, "sum"),
                "avg_credit": _format_agg(avg_cred, "avg"),
                "avg_debit": _format_agg(avg_deb, "avg"),
                "counts": _get_monthly_counts(moves),
            },
        )
        mail.send_to(recipient)

        return HttpResponse(f"Summary sent to {recipient}!", status=200)
