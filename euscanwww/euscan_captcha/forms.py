from captcha.fields import ReCaptchaField
from registration.forms import RegistrationForm
from django.conf import settings

class RegistrationFormCaptcha(RegistrationForm):
    captcha = ReCaptchaField(
        public_key=settings.RECAPTCHA_PUBLIC_KEY,
        private_key=settings.RECAPTCHA_PRIVATE_KEY,
        use_ssl=True,
        attrs={'theme': 'white'})
