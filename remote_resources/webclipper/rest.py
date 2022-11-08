from rest_framework import serializers


class BaseWebClipSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'page_url',
            'page_title',
            'html_content',
        )


__all__ = (
    'BaseWebClipSerializer',
)
