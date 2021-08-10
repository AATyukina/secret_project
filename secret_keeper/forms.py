from django import forms


class SaveSecretForm(forms.Form):
    secret_field = forms.CharField(label="Enter your message here")


class ReturnSecretForm(forms.Form):
    access_token_field = forms.CharField(label="Enter your access token here")

