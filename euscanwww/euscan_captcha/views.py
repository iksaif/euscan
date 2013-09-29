from registration.backends.default.views import RegistrationView
from forms import RecaptchaRegistrationForm

class RecaptchaRegistrationView(RegistrationView):
    form_class = RecaptchaRegistrationForm
