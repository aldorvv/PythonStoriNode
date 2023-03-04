import csv
import json
from datetime import datetime

from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from moves.models import Move
from utils import MediaStorage

from .models import Account
from .serializers import AccountSerializer

STORAGE = MediaStorage()


def _parse_date(str_date, fmt="%m/%d"):
    date_ = datetime.strptime(str_date, fmt).replace(year=datetime.today().year)
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
