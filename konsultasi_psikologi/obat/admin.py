from django.contrib import admin
from .models import Resep, ResepItem, ObatOrder

class ResepItemInline(admin.TabularInline):
    model = ResepItem
    extra = 0

@admin.register(Resep)
class ResepAdmin(admin.ModelAdmin):
    list_display = ('id','pasien','konselor','tanggal')
    inlines = [ResepItemInline]

@admin.register(ObatOrder)
class ObatOrderAdmin(admin.ModelAdmin):
    list_display = ('id','resep','pasien','tanggal_order','metode','status','total')
