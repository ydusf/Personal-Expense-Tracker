from django.core.management.base import BaseCommand
from base.models import ExpenseCategory
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates expense categories in the database'

    def handle(self, *args, **options):
        categories = settings.CATEGORIES

        for category in categories:
            ExpenseCategory.objects.get_or_create(name=category[0], description=category[1])
            self.stdout.write(self.style.SUCCESS(f'Successfully created category: {category[0]} | {category[1]}'))
