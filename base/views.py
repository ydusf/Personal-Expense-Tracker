from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.safestring import mark_safe
from .forms import CustomUserCreationForm, ExpenseSearchForm, ProfileUpdateForm, ExpenseUpdateForm, GeneralBudgetUpdateForm, BudgetUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .models import *
import json
from .decorators import guest_only
from django.db.models import Q, ExpressionWrapper, FloatField, F
from django.contrib import messages
from django.urls import reverse
from .utils import convert_currency, get_exchange_rates
from django.conf import settings
from forex_python.converter import CurrencyCodes
from django.core.serializers.json import DjangoJSONEncoder
from .utils import create_expense_dict, convert_expenses_currency, calculate_budget_monitoring_data, calculate_top_spender_data, calculate_monthly_expenses_data
from datetime import date

@login_required(login_url="/login")
def home(request, chart_time_frequency=30):
    user = request.user

    currency_symbol = CurrencyCodes().get_symbol(user.profile.preferred_currency)

    expenses = Expense.objects.filter(user=user)
    expression = ExpressionWrapper(F('amount') / F('recurrence_frequency') * chart_time_frequency, output_field=FloatField())
    category_amount_dict = create_expense_dict(expenses=expenses, expression=expression)

    remaining_budget = round(user.generalbudget.remaining_budget / 365 * chart_time_frequency, 1)
        
    expense_categories = list(category_amount_dict.keys())
    expense_amounts = list(category_amount_dict.values())
    total_expenses = round(sum(expense_amounts), 1)

    expense_data = {
        'labels': expense_categories,
        'values': expense_amounts,
    }

    json_expense_data = json.dumps(expense_data)
    
    context = {
        'user': user,
        'expense_data': mark_safe(json_expense_data), 
        'total_expenses_amount': total_expenses,
        'remaining_budget': remaining_budget,
        'currency_symbol': currency_symbol,
    }

    return render(request, 'base/home.html', context)
    
@guest_only
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            username = form.cleaned_data['username']
            messages.success(request, f"{username}, your account has been successfully registered!")
            login(request, user)
            return redirect(reverse("home"))
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})

@login_required(login_url="/login")
def logout(request):
    logout(request)
    return redirect(reverse("login"))

@login_required(login_url="/login")
def expense_create(request):
    if request.method == "POST":
        form = ExpenseUpdateForm(request.POST)
        if form.is_valid():
            user = request.user
            expense = form.save(commit=False)
            expense.user = user
            expense.start_date = form.cleaned_data["start_date"]
            expense.end_date = form.cleaned_data["end_date"]
            if not expense.is_recurring:
              expense.recurrence_frequency = 365
              expense.recurrence_interval = 1
            expense.save()
            user.generalbudget.update_budget()
            messages.success(request, "Expense has been successfully created!")
            return redirect(reverse("expense_create"))
    else:
        form = ExpenseUpdateForm()

    return render(request, "base/expense_create.html", {"form": form})

@login_required(login_url="/login")
def expense_list(request):
    form = ExpenseSearchForm(request.GET)
    expenses = Expense.objects.filter(user=request.user)
    grouped_expenses = defaultdict(list)
    expense_type = request.GET.get('expense_type', 'all')

    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        expenses = expenses.filter(Q(category__name__icontains=search_query) | Q(category__description__icontains=search_query) | Q(description__icontains=search_query))

        if expense_type == 'recurring':
            expenses = expenses.filter(is_recurring=True)
        elif expense_type == 'discretionary':
            expenses = expenses.filter(is_recurring=False)

    for expense in expenses:
      if expense.end_date >= date.today():
        grouped_expenses[expense.category].append(expense)

    grouped_expenses = dict(grouped_expenses)

    context = {
        "grouped_expenses": grouped_expenses,
        "expense_type": expense_type
    }

    return render(request, "base/expense_list.html", context)


@login_required(login_url="/login")
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    request.user.generalbudget.update_budget()
    return redirect(reverse("expense_list"))

@login_required(login_url="/login")
def expense_edit(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == "POST":
        form = ExpenseUpdateForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            request.user.generalbudget.update_budget()
            messages.success(request, f"This expense has been successfully updated!")
            return redirect(reverse("expense_list"))        
    else:
        form = ExpenseUpdateForm(instance=expense)

    return render(request, "base/expense_edit.html", {"form": form})

@login_required(login_url="/login")
def category_list(request):
    category_list = ExpenseCategory.objects.all()
    return render(request, "base/category_list.html", {"category_list": category_list})

@login_required(login_url="/login")
def analytics(request):
    user = request.user
    remaining_budget = GeneralBudget.objects.get(user=user).remaining_budget
    currency_symbol = CurrencyCodes().get_symbol(user.profile.preferred_currency)
    expenses = Expense.objects.filter(user=user)
    
    # Creates dictionary of the monthly expenses for each category
    json_monthly_expense_data = json.dumps(calculate_monthly_expenses_data(expenses=expenses), cls=DjangoJSONEncoder)

    # Creates dictionary of the budget and corresponding expenses for each category
    json_budget_monitoring_data = json.dumps(calculate_budget_monitoring_data(user_budget=Budget.objects.filter(user=user), user=user), cls=DjangoJSONEncoder)

    # Creates reverse sorted dictionary of each category and its corresponding expenses
    json_top_spender_data = json.dumps(calculate_top_spender_data(expenses=expenses), cls=DjangoJSONEncoder)
    json_currency_symbol = json.dumps(currency_symbol)

    context = {
        'monthly_expense_data': mark_safe(json_monthly_expense_data),
        'budget_monitoring_data': mark_safe(json_budget_monitoring_data),
        'top_spender_data': mark_safe(json_top_spender_data),
        'remaining_budget': remaining_budget,
        'currency_symbol': mark_safe(json_currency_symbol),        
    }
    return render(request, "base/analytics.html", context)

@login_required(login_url="/login")
def profile(request):
    user = request.user
    return render(request, "base/profile.html", {"user": user})

@login_required(login_url="/login")
def profile_edit(request):
    user = request.user

    if request.method == "POST":
        # user_form = CustomUserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        user_previous_currency = user.profile.preferred_currency
        if profile_form.is_valid():
            # user_form.save()
            profile_form.save()

            user.profile.previous_currency = user_previous_currency
            user.profile.save()

            user_preferred_currency = user.profile.preferred_currency
            api_key = settings.API_KEY
            exchange_rates = get_exchange_rates(api_key)

            convert_expenses_currency(
                expenses=Expense.objects.filter(user=user), 
                prev_currency=user_previous_currency, 
                pref_currency=user_preferred_currency, 
                exchange_rates=exchange_rates
            )

            converted_amount = convert_currency(float(user.generalbudget.remaining_budget), user_previous_currency, user_preferred_currency, exchange_rates)
            user.generalbudget.remaining_budget = converted_amount
            user.generalbudget.save()

            messages.success(request, f"Your profile has been successfully updated!")
            return redirect(reverse("profile"))
    else:
        # user_form = CustomUserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=user.profile)

    context = {
        "user": user, 
        # "user_form": user_form, 
        "profile_form": profile_form,
    }

    return render(request, "base/profile_edit.html", context)

def budgets(request):
    user = request.user
    budgets = user.generalbudget.budgets.all()

    if request.method == 'POST':
        general_budget_form = GeneralBudgetUpdateForm(request.POST, instance=user.generalbudget)
        budget_form = BudgetUpdateForm(request.POST)
        if general_budget_form.is_valid():
            user.generalbudget.update_budget()
            general_budget_form.save()
            messages.success(request, f"Your total budget has been successfully updated!")
            return redirect(reverse("budgets"))
        elif budget_form.is_valid():
            category = budget_form.cleaned_data['category']
            amount = budget_form.cleaned_data['amount']
            
            # Check if a budget for the category already exists
            existing_budget = Budget.objects.filter(user=user, category=category).first()
            
            if existing_budget:
                # Update the existing budget
                existing_budget.amount = amount
                existing_budget.save()
                messages.success(request, f"You have successfully updated a budget for {category.name} to {amount}!")
            else:
                # Create a new budget if it doesn't exist
                budget = Budget(user=user, category=category, amount=amount)
                budget.save()
                user.generalbudget.budgets.add(budget)
                messages.success(request, f"You have successfully created a budget for {category.name} at {amount}!")

            user.generalbudget.update_total_budget()
            user.generalbudget.save()
            return redirect(reverse("budgets"))
    else:
        budget_form = BudgetUpdateForm()
        general_budget_form = GeneralBudgetUpdateForm(instance=user.generalbudget)

    context = {
        "budgets": budgets,
        "budget_form": budget_form,
        'general_budget_form': general_budget_form}

    return render(request, "base/budgets.html", context)
