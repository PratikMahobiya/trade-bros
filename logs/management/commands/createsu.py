from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='TradeBros').exists():
            User.objects.create_superuser(
                username='TradeBros',
                password='admin'
            )
        print('Superuser has been created.')