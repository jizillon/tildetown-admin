import re
import random

from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import Form, CharField, EmailField, Textarea, ChoiceField, BooleanField
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from .forms import TownieForm
from .models import Townie, Pubkey

SIGNUPS_ENABLED = True

class SignupView(FormView):
    form_class = TownieForm
    template_name = 'users/signup.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['signups_enabled'] = SIGNUPS_ENABLED
        return ctx


    @transaction.atomic
    def form_valid(self, form):
        del form.cleaned_data['captcha']
        del form.cleaned_data['aup']
        pubkey = Pubkey(key=form.cleaned_data.pop('pubkey'),
                        key_type=form.cleaned_data.pop('pubkey_type'))

        t = Townie(**form.cleaned_data)
        if not getattr(t, 'displayname'):
            t.displayname = t.username
        t.set_unusable_password()
        t.save()
        pubkey.townie = t
        pubkey.save()
        return redirect('users:thanks')


class ThanksView(TemplateView):
    template_name = 'users/thanks.html'

class KeyMachineView(TemplateView):
    template_name = 'users/keymachine.html'

class RandomView(View):
    def get(self, request):
        url = None
        users = list(Townie.objects.all())
        random.shuffle(users)
        for user in users:
            if user.has_modified_page():
                url = 'https://tilde.town/~{}'.format(user.username)
                break
        if url is None:
            url = 'https://tilde.town'

        return redirect(url)
