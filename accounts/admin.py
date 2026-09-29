from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Notification


# ─── Inline: UserProfile inside User ─────────────────────────────────────────
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '👤 Profile'
    fields = ('role', 'headline', 'bio', 'avatar')
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_role', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_role(self, obj):
        try:
            return obj.profile.role.title()
        except Exception:
            return '—'
    get_role.short_description = 'Role'


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ─── UserProfile ──────────────────────────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'headline', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'headline')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# ─── Notification ─────────────────────────────────────────────────────────────
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} ogeysiisood waxaa loo calaamadeeyay in la aqriyay.")
    mark_as_read.short_description = "✅ Calaamadee: La Aqriyay"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} ogeysiisood waxaa loo calaamadeeyay in aan la aqrin.")
    mark_as_unread.short_description = "🔔 Calaamadee: La Aqrin"
