# Generated by Django 4.1 on 2025-02-12 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cadastros", "0002_atividade"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="atividade",
            name="tempo",
        ),
    ]
