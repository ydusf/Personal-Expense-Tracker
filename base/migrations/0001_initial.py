# Generated by Django 4.2.5 on 2023-09-26 21:41

import base.models
import base.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("username", models.CharField(max_length=150, unique=True)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True, related_name="custom_users", to="auth.group"
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="custom_users_permissions",
                        to="auth.permission",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Budget",
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
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExpenseCategory",
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
                ("name", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
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
                    "image",
                    models.ImageField(
                        default="default_profile.png",
                        upload_to=base.utils.user_profile_image_upload_to,
                    ),
                ),
                ("forename", models.CharField(blank=True, max_length=30, null=True)),
                ("surname", models.CharField(blank=True, max_length=30, null=True)),
                ("job_title", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "income",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("biography", models.TextField(blank=True, null=True)),
                (
                    "preferred_currency",
                    models.CharField(
                        blank=True, default="USD", max_length=3, null=True
                    ),
                ),
                (
                    "previous_currency",
                    models.CharField(
                        blank=True, default="USD", max_length=3, null=True
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GeneralBudget",
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
                    "total_budget",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "remaining_budget",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                ("budgets", models.ManyToManyField(to="base.budget")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Expense",
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
                ("is_recurring", models.BooleanField(default=False)),
                (
                    "recurrence_frequency",
                    models.FloatField(
                        blank=True,
                        choices=[
                            (1, "Daily"),
                            (7, "Weekly"),
                            (30, "Monthly"),
                            (365, "Yearly"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "recurrence_interval",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("start_date", models.DateField(null=True)),
                ("end_date", models.DateField(null=True)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(0.01)],
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="base.expensecategory",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="budget",
            name="category",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="base.expensecategory",
            ),
        ),
        migrations.AddField(
            model_name="budget",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
