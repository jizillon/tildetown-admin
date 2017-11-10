from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('issue_status', 'issue_type', 'name', 'email')
    fields = ('name', 'email', 'issue_status', 'issue_type', 'issue_text')
