# tasks/forms.py

from django import forms

class UploadExcelForm(forms.Form):
    file = forms.FileField()

