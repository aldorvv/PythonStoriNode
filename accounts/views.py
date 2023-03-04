import csv
import json
from datetime import datetime as dt

from django.forms import ValidationError
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from moves.models import Move
from moves.serializers import MoveSerializer
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
        instance = self.get_object()
        recipient = request.query_params.get("email")
        if recipient is None:
            raise ValidationError("Please specify an email to send the summary")
        moves = Move.objects.filter(account=instance)
        ser = MoveSerializer(moves, many=True)

        deb_transactions = moves.filter(kind=-1)
        avg_deb = (
            sum(move.quantity for move in deb_transactions) / deb_transactions.count()
        )
        cred_transactions = moves.filter(kind=1)
        avg_cred = (
            sum(move.quantity for move in cred_transactions) / cred_transactions.count()
        )

        total = sum(move.quantity for move in moves)

        months = {
            1: "JAN",
            2: "FEB",
            3: "MAR",
            4: "APR",
            5: "MAY",
            6: "JUN",
            7: "JUL",
            8: "AUG",
            9: "SEP",
            10: "OCT",
            11: "NOV",
            12: "DEC",
        }

        monthly_counts = []
        for i in range(1, 13):
            current_month_count = moves.filter(date__month=i).count()
            monthly_counts.append(f"{current_month_count} movements in {months.get(i)}")

        summary_counts = "\n".join(monthly_counts)

        email = Email(
            "summary",
            f"Avg Cred: {avg_cred}\nAvg Deb: {avg_deb}\nTotal: {total}\n{summary_counts}",
        )
        email.send([recipient])
        return HttpResponse(f"Summary sent to {recipient}!", status=200)
