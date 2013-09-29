from django.conf.urls import patterns, url

from views import RecaptchaRegistrationView

urlpatterns = patterns(
    '', url(
        r'^register/$',
        RecaptchaRegistrationView.as_view(),
        name='registration_register'),
)
