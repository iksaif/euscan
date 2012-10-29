from django.conf.urls.defaults import patterns, url

from registration.views import register

urlpatterns = patterns('',
    url(
        r'^register/$',
        register,
        {'backend': 'euscanwww.captcha.CaptchaDefaultBackend'},
        name='registration_register'
    ),
)
