from django.contrib import admin
from .models import AllowedUser, AllowedGroup
# Register your models here.


class AllowedGroupInline(admin.StackedInline):
    model = AllowedGroup


@admin.register(AllowedUser)
class AllowedUserAdmin(admin.ModelAdmin):
    def groups_display(self, obj):
        return ", ".join([
            g.name for g in obj.groups.all()
        ])
    groups_display.short_description = "Groups"

    inlines= [AllowedGroupInline]
    list_display = ('username', 'groups_display', 'is_superuser', 'is_staff')
    filter_horizontal = ['groups']
