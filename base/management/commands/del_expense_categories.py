from django.core.management.base import BaseCommand
from base.models import ExpenseCategory
from django.conf import settings

class Command(BaseCommand):
    help = 'Deletes expense categories from the database'

    def handle(self, *args, **options):
        categories = settings.CATEGORIES

        for category in categories:
            try:
                category_obj = ExpenseCategory.objects.get(name=category[0], description=category[1])
                category_obj.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted category: {category[0]} | {category[1]}'))
            except ExpenseCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Category not found: {category[0]} | {category[1]}'))
