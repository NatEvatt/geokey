from django import forms
from django.utils.html import strip_tags

from .models import View


class ViewCreateForm(forms.ModelForm):
    """
    Validates the inputs against the model definition.
    Used in .views.ViewAdminCreateView
    """
    class Meta:
        model = View
        fields = ('name', 'description', 'isprivate')

    def clean(self):
        cleaned_data = super(ViewCreateForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data['name'])
        cleaned_data['description'] = strip_tags(cleaned_data['description'])

        return cleaned_data