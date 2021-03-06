from django.contrib.auth.models import User
from django.db.models import Model, TextField, EmailField, CharField, DateTimeField, ForeignKey

ISSUE_TYPE_CHOICES = (
    ('logging_in', 'help logging in'),
    ('concern_site', 'concern about the site'),
    ('concern_user', 'concern about another user'),
    ('package', 'install a package'),
    ('question', 'just a question',),
    ('other', 'something else'),
)

ISSUE_STATUS_CHOICES = (
    ('triage', 'to triage'),
    ('acked', 'acknowledged'),
    ('waiting', 'waiting to hear from submitter'),
    ('completed', 'nothing more to do'),
)


class Ticket(Model):
    submitted = DateTimeField(auto_now_add=True)
    name = CharField(blank=False, null=False, max_length=100)
    email = EmailField(blank=False, null=False)
    issue_type = CharField(choices=ISSUE_TYPE_CHOICES,
                           blank=False,
                           null=False,
                           max_length=50)
    issue_text = TextField(blank=False, null=False)
    issue_status = CharField(choices=ISSUE_STATUS_CHOICES,
                             blank=False,
                             null=False,
                             max_length=50,
                             default=ISSUE_STATUS_CHOICES[0][0])
    assigned = ForeignKey(User, blank=True, null=True, help_text="Assign this ticket to an admin or unassign it.")

    def __str__(self):
        return '{} from {}'.format(self.issue_type, self.name)


class Note(Model):
    created = DateTimeField(auto_now_add=True)
    body = TextField(blank=False, null=False)
    author = ForeignKey(User)
    ticket = ForeignKey(Ticket)

    def __str__(self):
        return "admin note"
