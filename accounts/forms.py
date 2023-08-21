

from django import forms
from django.contrib.auth.forms import SetPasswordForm,PasswordResetForm


class MyPasswordResetform(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))



class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='new password',widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))
    new_password2 = forms.CharField(label=' Confirm new password',widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))