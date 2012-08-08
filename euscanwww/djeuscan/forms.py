from django import forms

from djeuscan.models import Version, ProblemReport


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
