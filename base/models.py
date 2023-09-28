from django.db import models
from django.db.models import ExpressionWrapper, FloatField, F
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from PIL import Image
from .utils import user_profile_image_upload_to, create_expense_dict
from decimal import Decimal
from django.core.validators import MinValueValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='custom_users'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_users_permissions'
    )

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='default_profile.png', upload_to=user_profile_image_upload_to)
    forename = models.CharField(max_length=30, blank=True, null=True)
    surname = models.CharField(max_length=30, blank=True, null=True)
    job_title = models.CharField(max_length=50, blank=True, null=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    preferred_currency = models.CharField(max_length=3, blank=True, null=True, default='USD')
    previous_currency = models.CharField(max_length=3, blank=True, null=True, default='USD')

    def __str__(self):
        return f"{self.user.username} Profile"

    # def save(self, *args, **kwargs):
    #     super(Profile, self).save(*args, **kwargs)

    #     #Deletes old profile picture
    #     try:
    #         old_instance = Profile.objects.get(pk=self.pk)
    #         if old_instance.image != self.image and old_instance.image.name != 'default_profile.png':
    #             old_instance.image.delete()
    #     except Profile.DoesNotExist:
    #         pass

    #     #Resizes profile picture
    #     img = Image.open(self.image.path)

    #     max_width = 300
    #     max_height = 300

    #     if img.height > max_height or img.width > max_width:
    #         img.thumbnail((max_width, max_height))
    #         img.save(self.image.path)

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    custom_freq = [
        (1, 'Daily'), 
        (7, 'Weekly'), 
        (30, 'Monthly'), 
        (365, 'Yearly'),
    ]
    is_recurring = models.BooleanField(default=False)
    recurrence_frequency = models.FloatField(choices=custom_freq, max_length=10, blank=True, null=True)
    recurrence_interval = models.PositiveIntegerField(blank=True, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f'{self.category} - {self.description}'

class Budget(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, default=None)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.category.name} Budget'

class GeneralBudget(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budgets = models.ManyToManyField(Budget)

    def __str__(self):
        return f'{self.user.username} Budget'

    def update_budget(self):
        expenses = Expense.objects.filter(user=self.user)
        expression = ExpressionWrapper(F('amount') / F('recurrence_frequency') * 365, output_field=FloatField())
        category_amount_dict = create_expense_dict(expenses=expenses, expression=expression)
        total_expenses = Decimal(sum(category_amount_dict.values()))

        if total_expenses is None:
            total_expenses = Decimal('0.00')

        remaining_budget = self.total_budget - total_expenses
        self.remaining_budget = remaining_budget
        self.save()

    def update_total_budget(self):
        if self.budgets.count() > 0:
            if self.total_budget == 0:
                self.total_budget = sum([budget.amount for budget in self.budgets])
        self.save()