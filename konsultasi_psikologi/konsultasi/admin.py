from django.contrib import admin
from .models import Pembayaran

@admin.register(Pembayaran)
class PembayaranAdmin(admin.ModelAdmin):
    # Menampilkan kolom-kolom ini di list admin
    list_display = ('pasien', 'get_konselor', 'jumlah', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('pasien__nama',)

    # Helper untuk menampilkan nama konselor dari relasi booking
    def get_konselor(self, obj):
        if obj.booking and obj.booking.konselor:
            return obj.booking.konselor.nama
        return "-"
    get_konselor.short_description = 'Konselor'