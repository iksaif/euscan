from django import forms

from djeuscan.models import Version, ProblemReport, UserProfile


class WorldForm(forms.Form):
    world = forms.FileField()


class PackagesForm(forms.Form):
    packages = forms.CharField(widget=forms.Textarea)


class ProblemReportForm(forms.ModelForm):
    version = forms.ModelChoiceField(queryset=Version.objects.all(),
                                     empty_label="all", required=False)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 15})
    )

    def __init__(self, package, *args, **kwargs):
        super(ProblemReportForm, self).__init__(*args, **kwargs)
        self.fields["version"].queryset = Version.objects.filter(
            package=package
        )

    class Meta:
        model = ProblemReport
        fields = ('version', 'subject', 'message')


class PreferencesForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField()

    feed_upstream_info = forms.BooleanField(required=False,
                                            label="Upstream info")
    feed_portage_info = forms.BooleanField(required=False,
                                           label="Portage info")
    feed_show_adds = forms.BooleanField(required=False,
                                        label="Show version bumps")
    feed_show_removals = forms.BooleanField(required=False,
                                            label="Show version removals")
    feed_ignore_pre = forms.BooleanField(required=False,
                                         label="Ignore unstable releases")
    feed_ignore_pre_if_stable = forms.BooleanField(
        required=False,
        label="Ignore unstable releases if current version is stable"
    )

    email_activated = forms.BooleanField(
        required=False, label="Receive euscan emails"
    )
    email_every = forms.ChoiceField(
        choices=UserProfile.EMAIL_OPTS,
        label="Send email",
    )
    email_ignore_pre = forms.BooleanField(
        required=False, label="Ignore unstable releases"
    )
    email_ignore_pre_if_stable = forms.BooleanField(
        required=False,
        label="Ignore unstable releases if current version is stable"
    )
