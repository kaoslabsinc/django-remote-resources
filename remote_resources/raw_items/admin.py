from django.contrib import admin, messages


class RawItemAdmin(admin.ModelAdmin):
    actions = ('process',)

    @admin.display(boolean=True)
    def is_processed(self, obj):
        return obj.is_processed

    def get_queryset(self, request):
        qs = super(RawItemAdmin, self).get_queryset(request)
        return qs.annotate_is_processed()

    @admin.action
    def process(self, request, queryset):
        count_processed = queryset.process()
        messages.success(request, f"Processed {count_processed} items")
