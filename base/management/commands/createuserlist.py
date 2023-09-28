from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'List users in the PostgreSQL database'

    def handle(self, *args, **options):
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT usename FROM pg_user;')
            users = cursor.fetchall()

        self.stdout.write(self.style.SUCCESS('Users in the PostgreSQL database:'))
        for user in users:
            self.stdout.write(user[0])
