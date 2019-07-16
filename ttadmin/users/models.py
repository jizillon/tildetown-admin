import logging
import os
from subprocess import run, CalledProcessError
from tempfile import TemporaryFile

from django.db.models import Model
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import TextField, BooleanField, CharField, ForeignKey
from django.template.loader import get_template

from common.mailing import send_email
from help.models import Ticket

logger = logging.getLogger()

SSH_TYPE_CHOICES = (
    ('ssh-rsa', 'ssh-rsa',),
    ('ssh-dss', 'ssh-dss',),
    ('ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp256'),
)

DEFAULT_INDEX_PATH = '/etc/skel/public_html/index.html'

if os.path.exists(DEFAULT_INDEX_PATH):
    DEFAULT_INDEX_PAGE = open(DEFAULT_INDEX_PATH).read().rstrip()
else:
    logger.warning('No default html page found in skel. using empty string.')
    DEFAULT_INDEX_PAGE = ''


KEYFILE_HEADER = """########## GREETINGS! ##########
# Hi! This file is automatically managed by tilde.town. You
# seriously shouldn't change it. If you want to add more public keys that's
# totally fine: you can put them in ~/.ssh/authorized_keys"""


class Townie(User):
    """Both an almost normal Django User as well as an abstraction over a
    system user."""
    class Meta:
        verbose_name = 'Townie'
        verbose_name_plural = 'Townies'

    # the actual values here have a leading int for sorting :(
    UNREVIEWED = '0_unreviewed'
    TEMPBAN    = '1_tempban'
    ACCEPTED   = '2_accepted'
    REJECTED   = '3_rejected'
    PERMABAN   = '4_permaban'
    STATE_CHOICES = (
            (REJECTED, 'Rejected'),
            (ACCEPTED, 'Accepted'),
            (UNREVIEWED, 'Unreviewed'),
            (PERMABAN, 'Permanently Banned'),
            (TEMPBAN, 'Temporarily Banned'),
    )
    shell = CharField(max_length=50, default="/bin/bash")
    state = CharField(max_length=20, choices=STATE_CHOICES, default=UNREVIEWED)
    reasons = TextField(blank=True, null=False, default='')
    plans = TextField(blank=True, null=False, default='')
    socials = TextField(blank=True, null=False, default='')
    referral = CharField(max_length=100, null=True, blank=True)
    displayname = CharField(max_length=100, blank=False, null=False)
    notes = TextField(blank=True, null=True,
          help_text='Use this field to share information about this user (reviewed or not) for other admins to see')

    @property
    def accepted(self):
        return self.ACCEPTED == self.state

    @property
    def unreviewed(self):
        return self.UNREVIEWED == self.state

    @property
    def home(self):
        return os.path.join('/home', self.username)

    def send_welcome_email(self):
        welcome_tmpl = get_template('users/welcome_email.txt')
        context = {
            'username': self.username,
            'admin_name': 'vilmibm',
        }
        text = welcome_tmpl.render(context)
        success = send_email(self.email, text, subject='tilde.town!')
        if not success:
            Ticket.objects.create(name='system',
                                  email='root@tilde.town',
                                  issue_type='other',
                                  issue_text='was not able to send welcome email to {} ({})'.format(
                                      self.username,
                                      self.email))

    # managing concrete system state
    def has_modified_page(self):
        """Returns whether or not the user has modified index.html. If they
        don't have one, returns False."""
        index_path = os.path.join(self.home, 'public_html/index.html')
        if not os.path.exists(index_path):
            return False

        index_page = open(index_path).read().rstrip()
        return index_page != DEFAULT_INDEX_PAGE

    def create_on_disk(self):
        """A VERY NOT IDEMPOTENT create function. Originally, I had ambitions
        to have this be idempotent and able to incrementally update a user as
        needed, but decided that was overkill for now."""
        assert(self.accepted)
        dot_ssh_path = '/home/{}/.ssh'.format(self.username)

        error = _guarded_run(['sudo',
                              'adduser',
                              '--quiet',
                              '--shell={}'.format(self.shell),
                              '--gecos="{}"'.format(self.displayname),
                              '--disabled-password',
                              self.username])
        if error:
            logger.error(error)
            return

        error = _guarded_run(['sudo',
                              'usermod',
                              '-a',
                              '-Gtown',
                              self.username])

        if error:
            logger.error(error)
            return

        # Create .ssh
        error = _guarded_run(['sudo',
                              '--user={}'.format(self.username),
                              'mkdir',
                              dot_ssh_path])
        if error:
            logger.error(error)
            return

    def write_authorized_keys(self):
        # Write out authorized_keys file
        # Why is this a call out to a python script? There's no secure way with
        # sudoers to allow this code to write to a file; if this code was to be
        # compromised, the ability to write arbitrary files with sudo is a TKO.
        # By putting the ssh key file creation into its own script, we can just
        # give sudo access for that one command to this code.
        #
        # We could put the other stuff from here into that script and then only
        # grant sudo for the script, but then we're moving code out of this
        # virtual-env contained, maintainable thing into a script. it's my
        # preference to have the script be as minimal as possible.
        with TemporaryFile(dir="/tmp") as fp:
            fp.write(self.generate_authorized_keys().encode('utf-8'))
            fp.seek(0)
            error = _guarded_run(['sudo',
                                  '--user={}'.format(self.username),
                                  '/town/src/tildetown-admin/scripts/create_keyfile.py',
                                  self.username],
                                 stdin=fp)
            if error:
                logger.error(error)

    def generate_authorized_keys(self):
        """returns a string suitable for writing out to an authorized_keys
        file"""
        content = KEYFILE_HEADER
        for pubkey in self.pubkey_set.all():
            prefix = pubkey.key.split(' ')
            prefix = prefix[0] if len(prefix) > 0 else None
            if prefix in [p[0] for p in SSH_TYPE_CHOICES]:
                content += '\n{}'.format(pubkey.key)
            else:
                content += '\n{} {}'.format(pubkey.key_type, pubkey.key)

        return content

    def rename_on_disk(self, old_username):
        """Assuming that this instance has a new name set, renames this user on
        disk with self.username."""
        # TODO use systemd thing to end their session
        error = _guarded_run([
            'sudo',
            '/town/src/tildetown-admin/scripts/rename_user.py',
            old_username,
            self.username])
        if error:
            logger.error(error)
            return
        logger.info('Renamed {} to {}'.format(old_username, self.username))

        # send user an email

        rename_tmpl = get_template('users/rename_email.txt')
        context = {
            'old_username': old_username,
            'new_username': self.username
        }
        text = rename_tmpl.render(context)
        success = send_email(self.email, text, subject='Your tilde.town user has been renamed!')
        if not success:
            Ticket.objects.create(name='system',
                                  email='root@tilde.town',
                                  issue_type='other',
                                  issue_text='was not able to send rename email to {} ({})'.format(
                                      self.username,
                                      self.email))


class Pubkey(Model):
    key_type = CharField(max_length=50,
                         blank=False,
                         null=False,
                         choices=SSH_TYPE_CHOICES)
    key = TextField(blank=False, null=False)
    townie = ForeignKey(Townie)


@receiver(post_save, sender=Pubkey)
def on_pubkey_post_save(sender, instance, **kwargs):
    # Ensure we're checking the townie as it exists at the point of pubkey
    # save. If a user is being reviewed, we'll write their key file in the
    # townie pre save.
    townie = Townie.objects.filter(username=instance.townie.username)
    if not townie:
        return

    townie = townie[0]

    if townie.accepted:
        townie.write_authorized_keys()


@receiver(pre_save, sender=Townie)
def on_townie_pre_save(sender, instance, **kwargs):
    if instance.id is None:
        logger.info('Signup from {}'.format(instance.username))
        return

    existing = Townie.objects.get(id=instance.id)

    # See if we need to create the user on disk.
    if existing.unreviewed and instance.accepted:
        logger.info('Creating user {} on disk.'.format(instance.username))
        instance.create_on_disk()
        instance.send_welcome_email()
        instance.write_authorized_keys()
        return
    else:
        # This user state transition is currently undefined. In the future, we can check for things
        # like bans/unbans and then take the appropriate action.
        return

    # See if this user needs a rename on disk
    logger.info('checking for rename {} vs {}'.format(
        existing.username, instance.username))
    if existing.username != instance.username:
        logger.info('username do not match, going to rename')
        instance.rename_on_disk(existing.username)


def _guarded_run(cmd_args, **run_args):
    """Given a list of args representing a command invocation as well as var
    args to pass onto subprocess.run, run the command and check for an error.
    if there is one, files a helpdesk ticket and returns it. Returns None on
    success."""
    try:
        run(cmd_args,
            check=True,
            **run_args)
    except CalledProcessError as e:
        Ticket.objects.create(name='system',
                              email='root@tilde.town',
                              issue_type='other',
                              issue_text='error while running {}: {}'.format(
                                  cmd_args, e))
        return e
