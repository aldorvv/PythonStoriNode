# Generated by Django 4.1.7 on 2023-03-04 20:56

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Move",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("kind", models.IntegerField()),
                ("quantity", models.FloatField()),
            ],
            options={
                "db_table": "moves",
            },
        ),
    ]
