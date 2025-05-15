from django.contrib import admin
from .models import CryptoToken
from django.utils import timezone

# Register your models here.

class CryptoTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "key", "is_expired"]
    fields = []
    raw_id_fields = ["user",]

    def is_expired(self, obj):
        return obj.expiry < timezone.now()

admin.site.register(CryptoToken, CryptoTokenAdmin)

