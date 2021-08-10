from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms import Form

from secret_keeper.forms import SaveSecretForm, ReturnSecretForm
from secret_keeper.access_key_generator import generate_access_key
from secret_keeper.models import Secret


class SecretGeneralView(View):
    form_class: Form = Form
    initial: dict
    template_name: str = "secret_keeper/general_view.html"
    # where token or secret will be saved to transfer to another view
    session_field_name: str
    good_redirect_to: str
    error_message: str

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.initial)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                result = self.action(form)
            except Exception:
                pass
            else:
                request.session[self.session_field_name] = result
                return HttpResponseRedirect(reverse(self.good_redirect_to))
        params = {
            'form': form,
            'data_to_show': {
                'text': self.error_message
            }
        }
        return render(request, self.template_name, params)

    def action(self, form):
        raise NotImplemented


class SecretSaver(SecretGeneralView):
    form_class: Form = SaveSecretForm
    initial: dict = {'form': form_class}
    session_field_name: str = "generated_token"
    good_redirect_to: str = 'secret_keeper:save_success'
    error_message: str = "Form isn't valid or something went wrong during saving!"

    def action(self, form):
        access_key = generate_access_key()
        Secret.objects.create_secret(
            user_access_key=access_key, secret=form.cleaned_data["secret_field"]
        )
        return access_key


class SecretGiver(SecretGeneralView):
    form_class: Form = ReturnSecretForm
    initial: dict = {'form': form_class}
    session_field_name: str = "secret"
    good_redirect_to: str = 'secret_keeper:return_success'
    error_message: str = "Incorrect access token or something went wrong!"

    def action(self, form):
        secret = Secret.objects.return_secret(user_access_key=form.cleaned_data["access_token_field"])
        return secret


class SuccessActionGeneral(View):
    template_name: str
    session_field_name: str
    # redirect in case of error - no value found in session
    bad_redirect_to: str

    def get(self, request, *args, **kwargs):
        try:
            params = {"value": request.session.pop(self.session_field_name)}
            return render(request, self.template_name, params)
        except KeyError:
            return HttpResponseRedirect(reverse(self.bad_redirect_to))


class SuccessSave(SuccessActionGeneral):
    template_name = "secret_keeper/save_success.html"
    session_field_name = 'generated_token'
    bad_redirect_to = 'secret_keeper:save'


class SuccessReturn(SuccessActionGeneral):
    template_name = "secret_keeper/return_success.html"
    session_field_name = 'secret'
    bad_redirect_to = 'secret_keeper:return'

