from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home", views.home, name="home"),
    path("home/<int:chart_time_frequency>/", views.home, name="home"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    path("expense_create", views.expense_create, name="expense_create"),
    path("expense_list", views.expense_list, name="expense_list"),
    path("expense_edit/<int:expense_id>/", views.expense_edit, name="expense_edit"),
    path("expenses/<int:expense_id>/delete/", views.delete_expense, name="delete_expense"),
    path("category_list", views.category_list, name="category_list"),
    path("analytics", views.analytics, name="analytics"),
    path("profile", views.profile, name="profile"),
    path("profile_edit", views.profile_edit, name="profile_edit"),
    path("budgets", views.budgets, name="budgets")
]