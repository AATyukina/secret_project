from secret_keeper.views import SecretSaver, SecretGiver, SuccessSave, SuccessReturn
from django.urls import path

urlpatterns = [
    path(r'save_secret', SecretSaver.as_view(), name="save"),
    path(r'return_secret', SecretGiver.as_view(), name="return"),
    path(r'save_success', SuccessSave.as_view(), name="save_success"),
    path(r'return_success', SuccessReturn.as_view(), name="return_success")
]