from building_blocks.admin import SluggedKaosModelAdmin, ArchivableMixinAdmin
from building_blocks.consts.field_names import *
from django.contrib import admin

from .models import Form, FormField, ClipperEndpoint


class FormFieldInline(
    admin.StackedInline
):
    slug_source = 'name'
    model = FormField
    extra = 0
    ordering = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    fields = (
        'order',
        (NAME, SLUG,),
        TYPE,
        ('choices', 'choices_endpoint')
    )


@admin.register(Form)
class FormAdmin(
    SluggedKaosModelAdmin
):
    inlines = (FormFieldInline,)


@admin.register(ClipperEndpoint)
class ClipperEndpointAdmin(
    ArchivableMixinAdmin,
    SluggedKaosModelAdmin
):
    list_display = (NAME, SLUG, *ArchivableMixinAdmin.list_display)
    readonly_fields = (
        *SluggedKaosModelAdmin.readonly_fields,
        *ArchivableMixinAdmin.readonly_fields,
    )
    autocomplete_fields = ('form',)
    fieldsets = (
        (None, {'fields': (NAME, 'post_endpoint', 'form')}),
        *SluggedKaosModelAdmin.fieldsets[1:],
    )
