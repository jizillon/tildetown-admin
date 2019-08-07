from django.conf.urls import url
from django.contrib import admin
from django.forms import ModelForm
from .models import Ticket, Note, EmailTemplate


class ImmutableNoteInline(admin.TabularInline):
    model = Note
    extra = 1
    max_num = 0
    fields = ('author', 'created', 'body')
    readonly_fields = ('author', 'created', 'body')
    can_delete = False
    ordering = ('created',)


class NewNoteInline(admin.StackedInline):
    model = Note
    extra = 0
    fields = ('body',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.none()


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    fields = ('name', 'body')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [ImmutableNoteInline, NewNoteInline]
    readonly_fields = ('submitted', 'issue_type')
    list_display = ('submitted', 'issue_status', 'assigned', 'issue_type', 'name', 'email',)
    list_filter = ('issue_status', 'issue_type', 'assigned')
    fields = ('submitted', 'name', 'email', 'assigned', 'issue_status', 'issue_type', 'issue_text')

    change_form_template = "admin/ticket_with_email.html"

    def save_related(self, request, form, formsets, change):
        # THIS IS EXTREMELY BOOTLEG AND MAY BREAK IF MORE INLINES ARE ADDED TO THIS ADMIN.
        for formset in formsets:
            if len(formset.forms) == 1:
                # It's probably the add new note form (i hope).
                note_form = formset.forms[0]
                note_form.instance.author = request.user
                note_form.instance.save()
                note_form.save(commit=False)
                note_form.save_m2m()
        return super().save_related(request, form, formsets, change)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['email_templates'] = EmailTemplate.objects.all()
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
                url(r'emails/send$', self.admin_site.admin_view(self.send_email_view)),
                ]
        return urls + custom_urls


    def send_email_view(self, request):
        pass



