from django import forms
from django.forms import TextInput
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St'
    }))
    apartment_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite'
    }))
    shipping_country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(
        attrs={'class':'custom-select d-block w-100'
    }))
    zip = forms.CharField(widget=TextInput(attrs={
        'class':'custom-select d-block w-100',
        'id': 'zip'
    }))
    same_shipping_address = forms.BooleanField(widget=forms.CheckboxInput())
    save_info = forms.BooleanField(widget=forms.CheckboxInput())
    _option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=_CHOICES)

    # shipping_address = forms.CharField(required=False)
    # shipping_address2 = forms.CharField(required=False)
    # shipping_country = CountryField(blank_label='(select country)').formfield(
    #     required=False,
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100',
    #     }))
    # shipping_zip = forms.CharField(required=False)
    #
    # billing_address = forms.CharField(required=False)
    # billing_address2 = forms.CharField(required=False)
    # billing_country = CountryField(blank_label='(select country)').formfield(
    #     required=False,
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100',
    #     }))
    # billing_zip = forms.CharField(required=False)
    #
    # same_billing_address = forms.BooleanField(required=False)
    # set_default_shipping = forms.BooleanField(required=False)
    # use_default_shipping = forms.BooleanField(required=False)
    # set_default_billing = forms.BooleanField(required=False)
    # use_default_billing = forms.BooleanField(required=False)
    #
    # _option = forms.ChoiceField(
    #     widget=forms.RadioSelect, choices=_CHOICES)


class ContactForm(forms.Form):
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)