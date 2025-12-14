from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# Une classe Mixin pour appliquer le style Tailwind à tous les champs
class TailwindStyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-lg bg-slate-50 border border-slate-300 focus:border-aegis-500 focus:ring-2 focus:ring-aegis-200 outline-none transition duration-200 text-slate-700 placeholder-slate-400',
                'placeholder': field.label
            })

class UserRegisterForm(TailwindStyleMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email') # Ajoute d'autres champs si besoin

class UserLoginForm(TailwindStyleMixin, AuthenticationForm):
    pass
