from django import forms

class WorldFileForm(forms.Form):
    world_file = forms.FileField()

class WorldForm(forms.Form):
    world = forms.CharField(widget=forms.Textarea)
