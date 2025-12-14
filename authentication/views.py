from django.contrib.auth import login
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework.authtoken.models import Token
from .forms import UserRegisterForm, UserLoginForm
from packages.models import Package


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('index') # Redirige vers l'accueil après login


class RegisterView(CreateView):
    template_name = 'authentication/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome to Aegis Registry, {user.username}!")
        return redirect(self.success_url)
    

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'authentication/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupère ou crée le token pour l'utilisateur courant
        token, _ = Token.objects.get_or_create(user=self.request.user)
        context['api_token'] = token.key
        
        # Récupère les paquets de l'utilisateur
        context['my_packages'] = Package.objects.filter(author=self.request.user).order_by('-updated_at')
        
        return context

    def post(self, request, *args, **kwargs):
        # Action pour régénérer le token
        if 'regenerate_token' in request.POST:
            # Supprime l'ancien
            Token.objects.filter(user=request.user).delete()
            # En crée un nouveau
            Token.objects.create(user=request.user)
            messages.success(request, "Your API Token has been regenerated.")
            return redirect('profile')
        
        return self.get(request, *args, **kwargs)