# Generated by Django 5.0.6 on 2024-06-20 09:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("option", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyRecord",
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
                ("date", models.DateField(blank=True, null=True, verbose_name="DATE")),
                (
                    "day",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="DAY"
                    ),
                ),
                (
                    "expiry_index",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        null=True,
                        verbose_name="Expiry Index",
                    ),
                ),
                (
                    "total_entry",
                    models.BigIntegerField(default=0, verbose_name="Total Entry"),
                ),
                ("p_l", models.FloatField(default=0, verbose_name="P/L(%)")),
                (
                    "daily_max_profit",
                    models.FloatField(default=0, verbose_name="Daily Max-Profit"),
                ),
                ("daily_max_profit_time", models.DateTimeField(blank=True, null=True)),
                (
                    "daily_max_loss",
                    models.FloatField(default=0, verbose_name="Daily Max-Loss"),
                ),
                ("daily_max_loss_time", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Index",
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
                ("index", models.CharField(max_length=200, verbose_name="Index")),
                (
                    "index_symbol",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Index Symbol"
                    ),
                ),
                ("target", models.FloatField(default=9, verbose_name="Target(%)")),
                ("stoploss", models.FloatField(default=30, verbose_name="Stoploss(%)")),
                (
                    "fixed_target",
                    models.FloatField(default=30, verbose_name="Fixed Target(%)"),
                ),
                ("min_price", models.FloatField(default=0, verbose_name="Min Price")),
                ("max_price", models.FloatField(default=200, verbose_name="Max Price")),
                (
                    "trailing_target",
                    models.BooleanField(default=False, verbose_name="Trailing Target"),
                ),
                (
                    "expiry_date",
                    models.DateField(blank=True, null=True, verbose_name="Expiry Date"),
                ),
                ("pivot", models.FloatField(default=0, verbose_name="Pivot")),
                ("r1", models.FloatField(default=0, verbose_name="R1")),
                ("s1", models.FloatField(default=0, verbose_name="S1")),
                ("r2", models.FloatField(default=0, verbose_name="R2")),
                ("s2", models.FloatField(default=0, verbose_name="S2")),
                ("r3", models.FloatField(default=0, verbose_name="R3")),
                ("s3", models.FloatField(default=0, verbose_name="S3")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
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
                (
                    "mode",
                    models.CharField(
                        choices=[("CE", "Call"), ("PE", "Put"), ("none", "N/A")],
                        default="none",
                        max_length=50,
                        verbose_name="MODE",
                    ),
                ),
                ("index", models.CharField(max_length=200, verbose_name="INDEX")),
                ("symbol", models.CharField(max_length=200, verbose_name="SYMBOL")),
                ("indicate", models.CharField(max_length=50, verbose_name="INDICATE")),
                ("type", models.CharField(max_length=50, verbose_name="TYPE")),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("price", models.FloatField(verbose_name="PRICE")),
                ("stoploss", models.FloatField(verbose_name="STOPLOSS")),
                ("target", models.FloatField(verbose_name="TARGET")),
                (
                    "fixed_target",
                    models.FloatField(
                        blank=True, default=0, null=True, verbose_name="Fixed Target"
                    ),
                ),
                (
                    "profit",
                    models.FloatField(
                        blank=True, default=0, null=True, verbose_name="PROFIT (%)"
                    ),
                ),
                (
                    "max",
                    models.FloatField(
                        blank=True, default=0, null=True, verbose_name="MAX-P (%)"
                    ),
                ),
                ("max_l", models.FloatField(default=0, verbose_name="MAX-L (%)")),
                (
                    "highest_price",
                    models.FloatField(default=0, verbose_name="HIGHEST PRICE"),
                ),
                (
                    "order_id",
                    models.CharField(
                        blank=True,
                        default="0",
                        max_length=255,
                        null=True,
                        verbose_name="ORDER ID",
                    ),
                ),
                ("order_status", models.TextField(verbose_name="ORDER STATUS")),
                ("lot", models.FloatField(verbose_name="LOT")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="OptionSymbol",
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
                ("strike_price", models.BigIntegerField(verbose_name="Strike Price")),
                (
                    "symbol",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="SYMBOL"
                    ),
                ),
                (
                    "call_token",
                    models.CharField(
                        max_length=100, verbose_name="Angel One Call TOKEN"
                    ),
                ),
                (
                    "put_token",
                    models.CharField(
                        max_length=100, verbose_name="Angel One Put TOKEN"
                    ),
                ),
                (
                    "call_angel_symbol",
                    models.CharField(
                        default="NONE",
                        max_length=100,
                        verbose_name="Angel One Call Symbol",
                    ),
                ),
                (
                    "put_angel_symbol",
                    models.CharField(
                        default="NONE",
                        max_length=100,
                        verbose_name="Angel One Put Symbol",
                    ),
                ),
                ("lot", models.BigIntegerField(default=0, verbose_name="Lots")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "index",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="option.index",
                        verbose_name="Index",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StockConfig",
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
                (
                    "mode",
                    models.CharField(
                        choices=[("CE", "Call"), ("PE", "Put"), ("none", "N/A")],
                        default="none",
                        max_length=50,
                        verbose_name="MODE",
                    ),
                ),
                ("price", models.FloatField(default=0, verbose_name="PRICE")),
                ("stoploss", models.FloatField(default=0, verbose_name="STOPLOSS")),
                ("target", models.FloatField(default=0, verbose_name="TARGET")),
                (
                    "fixed_target",
                    models.FloatField(
                        blank=True, default=0, null=True, verbose_name="Fixed Target"
                    ),
                ),
                ("max", models.FloatField(default=0, verbose_name="MAX GAIN")),
                ("max_l", models.FloatField(default=0, verbose_name="MAX LOSS")),
                (
                    "highest_price",
                    models.FloatField(default=0, verbose_name="HIGHEST PRICE"),
                ),
                ("lot", models.FloatField(default=0, verbose_name="Lots")),
                (
                    "order_id",
                    models.CharField(
                        blank=True,
                        default="0",
                        max_length=255,
                        null=True,
                        verbose_name="ORDER ID",
                    ),
                ),
                (
                    "order_status",
                    models.TextField(default="NONE", verbose_name="ORDER STATUS"),
                ),
                (
                    "tr_hit",
                    models.BooleanField(default=False, verbose_name="Target Hit"),
                ),
                (
                    "trailing_sl",
                    models.FloatField(default=0, verbose_name="Trailing SL"),
                ),
                (
                    "ltp",
                    models.FloatField(
                        blank=True, default=0, null=True, verbose_name="Ltp"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "symbol",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="option.optionsymbol",
                    ),
                ),
            ],
        ),
    ]
