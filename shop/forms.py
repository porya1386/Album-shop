from django import forms


class ProductFilterForm(forms.Form):
    q = forms.CharField(
        required=False, max_length=100, label="Search",
        widget=forms.TextInput(attrs={
            "type": "search", "autocomplete": "off",
            "placeholder": "Search by name, price or year...",
        }),
    )
