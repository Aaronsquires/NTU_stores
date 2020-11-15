from django.contrib.auth import forms
from django.contrib.auth.models import User


class UserCreationForm(forms.UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name',
                  'last_name', 'email', 'is_active', 'is_superuser', 'groups',
                  'user_permissions']


class UserChangeForm(forms.UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'is_active', 'is_superuser', 'groups', 'user_permissions']
