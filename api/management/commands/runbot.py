from django.core.management.base import BaseCommand
from api.bot import main

class Command(BaseCommand):
    help = "Ejecuta el bot de Telegram"

    def handle(self, *args, **kwargs):
        main()
