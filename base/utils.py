import uuid
import os
import requests
from django.db.models import Sum, FloatField, F, ExpressionWrapper, Q
from datetime import date, timedelta

# Function to define the upload path for user profile images
def user_profile_image_upload_to(instance, filename):
    _, file_extension = os.path.splitext(filename)
    unique_filename = f'{uuid.uuid4()}{file_extension}'

    return f'profile_pics/{unique_filename}'

# Function to retrieve currency codes from an API
def get_currency_codes(api_key):
    response = requests.get(
        f"https://openexchangerates.org/api/currencies.json?app_id={api_key}")
    currency_codes = response.json()
    return sorted([(code, name) for code, name in currency_codes.items()], key=lambda x: x[1])

# Function to retrieve exchange rates from an API
def get_exchange_rates(api_key):
    response = requests.get(
        f"https://openexchangerates.org/api/latest.json?app_id={api_key}")
    exchange_rates = response.json().get("rates")
    return exchange_rates

# Function to convert currency based on exchange rates
def convert_currency(amount, from_currency, to_currency, exchange_rates):
    if from_currency == to_currency:
        return amount

    from_conversion_rate = exchange_rates[from_currency]
    to_conversion_rate = exchange_rates[to_currency]

    converted_amount = (amount / from_conversion_rate) * to_conversion_rate
    return converted_amount

# Function to create a dictionary of expenses aggregated by category
def create_expense_dict(expenses, expression):

    aggregated_expenses = expenses.annotate(adjusted_amount=expression).values(
        'category__name').annotate(total_amount=Sum('adjusted_amount'))

    exp_category_amount_dict = dict()

    for exp in aggregated_expenses:
        category_name = exp['category__name']
        total_amount = exp['total_amount']

        # Ensures total amount is not None
        if total_amount is None:
            total_amount = 0

        exp_category_amount_dict[category_name] = round(total_amount, 1)
    return exp_category_amount_dict

# Function to convert expenses currency
def convert_expenses_currency(expenses, prev_currency, pref_currency, exchange_rates):
    for exp in expenses:
        converted_amount = round(convert_currency(
            float(exp.amount), prev_currency, pref_currency, exchange_rates), 1)
        exp.amount = converted_amount
        exp.save()

# Function to calculate budget monitoring data
def calculate_budget_monitoring_data(user_budget, user):
    # Annotates user budgets with total expenses
    budgets = user_budget.annotate(
        total_expenses=Sum(
            ExpressionWrapper(F('category__expense__amount') * F(
                'category__expense__recurrence_interval'), output_field=FloatField()),
            filter=Q(category__expense__user=user),
            output_field=FloatField(),
        )
    )
    budget_dict = {budget.category.name: (
        budget.amount, budget.total_expenses) for budget in budgets}

    budget_monitoring_data = {
        'budget_monitoring_labels': list(budget_dict.keys()),
        'budget_monitoring_values': [tup[0] for tup in budget_dict.values()],
        'expense_monitoring_values': [tup[1] for tup in budget_dict.values()],
    }

    return budget_monitoring_data

# Function to calculate top spender data
def calculate_top_spender_data(expenses):
    expense_category_expression = ExpressionWrapper(F('category__expense__amount') * F(
        'category__expense__recurrence_interval'), output_field=FloatField())
    category_amount_dict = create_expense_dict(
        expenses=expenses, expression=expense_category_expression)
    sorted_expenses_dict = dict(
        sorted(category_amount_dict.items(), key=lambda x: x[1], reverse=True))

    top_spender_data = {
        'top_spenders_labels': list(sorted_expenses_dict.keys()),
        'top_spenders_values': list(sorted_expenses_dict.values()),
    }

    return top_spender_data

# Function to calculate monthly expenses data
def calculate_monthly_expenses_data(expenses):
    current_date = date.today()
    start_date = current_date - timedelta(days=365)

    monthly_expenses_dict = dict()

    while start_date <= current_date:
        end_date = start_date + timedelta(days=30)

        curr_month_expenses = expenses.filter(
            # Intersection with start_date and end_date
            Q(start_date__lte=end_date, end_date__gte=start_date) |
            # Start_date in the month, end_date is None (ongoing expense)
            Q(start_date__lte=end_date, end_date__isnull=True) |
            # End_date in the month, start_date is None (ongoing expense)
            Q(start_date__isnull=True, end_date__gte=start_date)
        ).aggregate(total=Sum('amount'))

        monthly_expenses_dict[start_date.strftime(
            '%B %y')] = curr_month_expenses['total']

        start_date = start_date + timedelta(days=30)

    context = {
        "monthly_expense_labels": list(monthly_expenses_dict.keys()),
        "monthly_expense_values": list(monthly_expenses_dict.values()),
    }

    return context
