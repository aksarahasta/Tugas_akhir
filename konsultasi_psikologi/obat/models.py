from django.db import models
from django.utils import timezone
from pasien.models import Pasien
from konselor.models import JadwalBooking  # booking/session
from logistik.models import Inventori

class Resep(models.Model):
    konsultasi = models.ForeignKey(
        JadwalBooking,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resep'
    )
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, related_name='resep')
    konselor = models.ForeignKey('konselor.Konselor', on_delete=models.SET_NULL, null=True, blank=True)
    tanggal = models.DateTimeField(default=timezone.now)
    catatan = models.TextField(blank=True)

    def __str__(self):
        return f"Resep #{self.pk} - {self.pasien.nama}"

    class Meta:
        ordering = ['-tanggal']


class ResepItem(models.Model):
    resep = models.ForeignKey(Resep, on_delete=models.CASCADE, related_name='items')
    inventori = models.ForeignKey(Inventori, on_delete=models.SET_NULL, null=True, blank=True)
    nama_obat = models.CharField(max_length=255)
    dosis = models.CharField(max_length=100, blank=True)
    jumlah = models.PositiveIntegerField(default=1)
    harga_satuan = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Jika inventori diset, ambil nama & harga dari inventori otomatis
        if self.inventori:
            # fallback attribute names if different
            nama = getattr(self.inventori, 'nama_item', None) or getattr(self.inventori, 'nama', None)
            harga = getattr(self.inventori, 'harga', None) or getattr(self.inventori, 'price', None) or getattr(self.inventori, 'harga_satuan', None)
            if nama:
                self.nama_obat = nama
            if harga is not None:
                self.harga_satuan = harga
        # jika nama_obat kosong - jangan biarkan (fallback)
        if not self.nama_obat and self.inventori:
            self.nama_obat = getattr(self.inventori, 'nama_item', '') or getattr(self.inventori, 'nama', '')

        super().save(*args, **kwargs)

    def subtotal(self):
        return self.jumlah * float(self.harga_satuan)

    def __str__(self):
        return f'{self.nama_obat} x {self.jumlah}'


class ObatOrder(models.Model):
    METODE_CHOICES = (
        ('ambil', 'Ambil di Klinik'),
        ('antar', 'Antar'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('diproses', 'Diproses'),
        ('dikirim', 'Dikirim'),
        ('selesai', 'Selesai'),
        ('batal', 'Batal'),
    )

    resep = models.ForeignKey(Resep, on_delete=models.CASCADE, related_name='orders')
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE)
    tanggal_order = models.DateTimeField(default=timezone.now)
    metode = models.CharField(max_length=10, choices=METODE_CHOICES, default='ambil')
    alamat_pengiriman = models.TextField(blank=True)
    jasa_pengiriman = models.CharField(max_length=200, blank=True)
    biaya_kurir = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total_obat = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def recalc_totals(self):
        items = self.resep.items.all()
        tot = sum(i.subtotal() for i in items)
        self.total_obat = tot
        self.total = tot + float(self.biaya_kurir or 0)
        return self.total

    def save(self, *args, **kwargs):
        self.recalc_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order #{self.pk} - {self.pasien.nama}'
