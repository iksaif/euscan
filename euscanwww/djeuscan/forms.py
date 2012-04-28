from django import forms


class WorldForm(forms.Form):
    world = forms.FileField()


class PackagesForm(forms.Form):
    packages = forms.CharField(widget=forms.Textarea)
