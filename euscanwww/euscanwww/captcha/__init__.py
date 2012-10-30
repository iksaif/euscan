from registration.backends.default import DefaultBackend
from forms import RegistrationFormCaptcha

class CaptchaDefaultBackend(DefaultBackend):
    def get_form_class(self, request):
        return RegistrationFormCaptcha
