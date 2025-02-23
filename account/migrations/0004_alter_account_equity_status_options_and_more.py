# Generated by Django 5.1.1 on 2024-10-07 09:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_accountconfiguration_equity_enabled_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account_equity_status',
            options={'verbose_name': 'Account Equity Entry', 'verbose_name_plural': 'Account Equity Entries'},
        ),
        migrations.AlterModelOptions(
            name='account_fno_status',
            options={'verbose_name': 'Account FnO Entry', 'verbose_name_plural': 'Account FnO Entries'},
        ),
    ]
