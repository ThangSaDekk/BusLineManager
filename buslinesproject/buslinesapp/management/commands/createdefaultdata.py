from django.db import transaction
from django.core.management.base import BaseCommand

from buslinesapp.models import Account


class Command(BaseCommand):
    help = "Create default data for models"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not Account.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.HTTP_INFO("Creating superuser..."))
            account = Account.objects.create_superuser(username="admin", password="thang123", email="thang111103@gmail.com")
            self.stdout.write(self.style.SUCCESS("Created superuser"))
