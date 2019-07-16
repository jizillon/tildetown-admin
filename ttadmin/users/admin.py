from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from .models import Townie, Pubkey
from common.social import post_users_to_social

class PubkeyInline(admin.TabularInline):
    model = Pubkey
    extra = 1

def bulk_accept(madmin, req, qs):
    for townie in qs:
        townie.state = 'accepted'
        townie.save()
    post_users_to_social(qs)

bulk_accept.short_description = 'mark selected townies as accepted'

def bulk_reject(madmin, req, qs):
    for townie in qs:
        townie.state = 'rejected'
        townie.save()

bulk_reject.short_description = 'mark selected townies as rejected'

@admin.register(Townie)
class TownieAdmin(admin.ModelAdmin):
    inlines = [PubkeyInline]
    list_display = ('username', 'state', 'email')
    readonly_fields = ('reasons', 'plans', 'socials')
    ordering = ('state',)
    exclude = ('first_name', 'last_name', 'password', 'groups', 'user_permissions', 'last_login', 'is_staff', 'is_active', 'is_superuser')
    actions = (bulk_accept, bulk_reject,)
    search_fields = ('username', 'email', 'displayname')
