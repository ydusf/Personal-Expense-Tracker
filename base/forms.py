from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ExpenseCategory, Profile, Expense, GeneralBudget, Budget
from django import forms
from datetime import datetime, timedelta
from django.conf import settings
from .utils import get_currency_codes


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    currency_codes = get_currency_codes(settings.API_KEY)
    preferred_currency = forms.ChoiceField(
        choices=currency_codes,
        initial='GBP')
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Profile
        fields = ['preferred_currency', 'image', 'forename', 'surname', 'job_title', 'income', 'biography']

class GeneralBudgetUpdateForm(forms.ModelForm):
    class Meta:
        model = GeneralBudget
        fields = ['total_budget']

class BudgetUpdateForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        label="Select Category",
        empty_label=None,
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="New Budget Amount"
    )

    class Meta:
        model = Budget
        fields = ["category", "amount"]

custom_freq = [
    (1, "Daily"), 
    (7, "Weekly"), 
    (30, "Monthly"), 
    (365, "Yearly"),
]

class ExpenseUpdateForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(),
        label="Select Category",
        empty_label=None,
    )

    is_recurring = forms.BooleanField(
        label="Recurring?",
        initial=False,
        required=False)

    recurrence_frequency = forms.ChoiceField(
        choices=custom_freq,
        label="Select Frequency",
        required=False
    )

    recurrence_interval = forms.IntegerField(
        label="Duration",
        help_text="Enter the number of intervals for which this expense will occur.",
        required=False
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Description"
    )

    def clean(self):
        cleaned_data = super().clean()
        frequency = int(cleaned_data.get("recurrence_frequency"))
        interval = cleaned_data.get("recurrence_interval")
        
        if frequency and interval is not None:
            start_date = datetime.today()
            end_date = start_date + timedelta(days=frequency * interval)
            
            cleaned_data["start_date"] = start_date
            cleaned_data["end_date"] = end_date
        else:
            start_date = datetime.today()
            end_date = start_date
            
            cleaned_data["start_date"] = start_date
            cleaned_data["end_date"] = end_date

        return cleaned_data

    class Meta:
        model = Expense
        fields = ["category", "is_recurring", "recurrence_frequency", "recurrence_interval", "amount", "description"]

class ExpenseSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search expenses'})
    )
