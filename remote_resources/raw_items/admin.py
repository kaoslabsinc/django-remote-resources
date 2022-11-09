from django.contrib import admin, messages


class ProcessedFilter(admin.SimpleListFilter):
    title = "is processed"
    parameter_name = 'is_processed'

    def lookups(self, request, model_admin):
        return [
            ('yes', "Yes"),
            ('no', "No"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(processed_item__isnull=False)
        if value == 'no':
            return queryset.filter(processed_item__isnull=True)


class RawItemAdmin(admin.ModelAdmin):
    actions = ('process',)
    list_filter = (ProcessedFilter,)
    readonly_fields = ('is_processed',)

    @admin.display(boolean=True, description="⚙️")
    def is_processed(self, obj):
        return obj.is_processed

    def get_queryset(self, request):
        qs = super(RawItemAdmin, self).get_queryset(request)
        return qs.annotate_is_processed()

    @admin.action
    def process(self, request, queryset):
        count_processed = queryset.process()
        messages.success(request, f"Processed {count_processed} items")
