from random import shuffle
import re

from django.core.exceptions import ValidationError
from django.forms import Form, CharField, EmailField, Textarea, ChoiceField, BooleanField
import sshpubkeys as ssh

from .models import Townie, SSH_TYPE_CHOICES
from common.forms import CaptchaField, throttler

submission_throttle = {}
throttle_submission = throttler(submission_throttle)


USERNAME_RE = re.compile(r'[a-z][a-z0-9_]+')
USERNAME_MIN_LENGTH = 3
DISPLAY_NAME_RE = re.compile(r"[a-zA-Z0-9_\-']+")
DISPLAY_MIN_LENGTH = 2


def validate_username(username):
    if len(username) < USERNAME_MIN_LENGTH:
        raise ValidationError('Username too short.')
    if not USERNAME_RE.match(username):
        raise ValidationError('Username must be all lowercase, start with a letter, and only use the _ special character')
    duplicate = Townie.objects.filter(username=username).count()
    if duplicate > 0:
        raise ValidationError('Username already in use :(')


def validate_displayname(display_name):
    if len(display_name) < DISPLAY_MIN_LENGTH:
        raise ValidationError('Display name too short.')
    if not DISPLAY_NAME_RE.match(display_name):
        raise ValidationError("Valid characters: a-z, A-Z, 0-9, -, _, and '.")


def validate_pubkey(pubkey):
    # TODO see if I can get the type out
    key = ssh.SSHKey(pubkey, strict_mode=False, skip_option_parsing=True)
    try:
        key.parse()
    except ssh.InvalidKeyException as e:
        raise ValidationError('Could not validate key: {}'.format(e))
    except NotImplementedError as e:
        raise ValidationError('Invalid key type')
    except Exception as e:
        raise ValidationError('unknown error: {}'.format(e))


class TownieForm(Form):
    username = CharField(
        validators=(validate_username,),
        help_text='lowercase and no spaces. underscore ok',
        label='username')

    email = EmailField(
        help_text='only used to message you about your account and nothing else.',
        label='e-mail')

    displayname = CharField(
        validators=(validate_displayname,),
        help_text='100% optional. pseudonyms welcome.',
        label='display name',
        required=False)

    referral = CharField(
       required=False,
       label='did a townie refer you? put their handle here.',
       help_text="this is optional and just helps us when reviewing your application.")

    reasons = CharField(
        widget=Textarea,
        required=True,
        label='what interests you about tilde.town?',
        help_text="""
        What about this intentional community intrigues you and makes you want to be a part of it?
        """.strip())

    plans = CharField(
        widget=Textarea,
        required=True,
        label='what sort of things do you want to do on tilde.town?',
        help_text="""
        Do you want to socialize? Make something? Learn stuff?
        """.strip())

    socials = CharField(
        widget=Textarea,
        required=False,
        label='where else are you online?',
        help_text="""Optional, but if you're comfortable sharing with us some links to other online
        spaces you're in (like twitter, mastodon, neocities, or whatever) we'd love to get to know
        you when reviewing your application.
        """.strip())

    captcha = CaptchaField()

    pubkey = CharField(
        widget=Textarea,
        validators=(validate_pubkey,),
        label='SSH public key',
        help_text='if this is not a thing you are familiar with, that\'s okay! you can make one <a href="/users/keymachine">here</a> or read <a href="https://tilde.town/wiki/getting-started/ssh.html">our guide</a> to learn more.')

    pubkey_type = ChoiceField(
        choices=SSH_TYPE_CHOICES,
        label='SSH public key type',
        help_text="unless you know what you're doing you can leave this be.")

    aup = BooleanField(
        label="i agree to the town's acceptable use policy",
        help_text='please read our <a href="https://tilde.town/wiki/conduct.html">code of conduct</a> and click this box if you agree.')

    def clean(self):
        result = super().clean()
        if self.errors:
            raise ValidationError('oops, looks like there were some problems below.')
        throttle_submission(self.cleaned_data['email'])
        return result
