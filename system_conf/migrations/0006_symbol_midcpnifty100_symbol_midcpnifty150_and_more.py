# Generated by Django 5.1.1 on 2024-10-03 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("system_conf", "0005_symbol_ltp_symbol_oi_symbol_percentchange_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="symbol",
            name="midcpnifty100",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="midcpnifty150",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="midcpnifty50",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="nifty100",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="nifty200",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="nifty50",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="smallcpnifty100",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="smallcpnifty250",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="symbol",
            name="smallcpnifty50",
            field=models.BooleanField(default=False),
        ),
    ]
