from django.contrib import admin
from .models import CryptoToken

# Register your models here.

class CryptoTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "key", "created", "expiry"]
    fields = []
    raw_id_fields = ["user",]

admin.site.register(CryptoToken, CryptoTokenAdmin)

