from django.contrib import admin
from django.forms import ModelForm
from .models import Ticket, Note

class NoteInline(admin.StackedInline):
    model = Note
    fields = ('created_at', 'body', 'author')
    readonly_fields = ('created_at', 'body', 'author')
    ordering = ('created_at',)
    extra = 1

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ('submitted',)
    list_display = ('submitted', 'issue_status', 'issue_type', 'name', 'email')
    list_filter = ('issue_status', 'issue_type')
    fields = ('submitted', 'name', 'email', 'issue_status', 'issue_type', 'issue_text')

    def save_related(request, form, formsets, change):
        for formset in formsets:
            import ipdb; ipdb.set_trace()
            pass # TODO set author based on request
        super()
