from django.db import models
from pasien.models import Pasien
from decimal import Decimal

# --- MODEL 1: KONSELOR ---
class Konselor(models.Model):
    nama = models.CharField(max_length=100)
    spesialisasi = models.CharField(max_length=200)
    no_hp = models.CharField(max_length=20)
    tarif_dasar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tarif_sesi = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.nama

# --- MODEL 2: JADWAL PRAKTEK (Slot Waktu) ---
# Perhatikan: Class ini TIDAK BOLEH punya field bernama 'jadwal' yang mengarah ke dirinya sendiri
class JadwalKonselor(models.Model):
    HARI_CHOICES = [
        ('Senin', 'Senin'),
        ('Selasa', 'Selasa'),
        ('Rabu', 'Rabu'),
        ('Kamis', 'Kamis'),
        ('Jumat', 'Jumat'),
        ('Sabtu', 'Sabtu'),
        ('Minggu', 'Minggu'),
    ]
    
    konselor = models.ForeignKey(Konselor, on_delete=models.CASCADE)
    # Ganti tanggal menjadi hari
    hari = models.CharField(max_length=10, choices=HARI_CHOICES)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()
    fokus = models.CharField(max_length=200)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.konselor.nama} - {self.hari}"

# --- MODEL 3: TRANSAKSI BOOKING ---
# Class inilah yang memanggil JadwalKonselor di atas
class JadwalBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Pembayaran'),
        ('terjadwal', 'Terjadwal'),
        ('selesai', 'Selesai'),
        ('batal', 'Batal'),
    ]

    # UBAH related_name AGAR TIDAK BENTROK DENGAN pasien.BookingRequest
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, related_name='jadwal_bookings')
    konselor = models.ForeignKey(Konselor, on_delete=models.CASCADE)
    
    # Field 'jadwal' menghubungkan Booking ini ke Slot JadwalKonselor
    # Karena JadwalKonselor sudah didefinisikan di atas, ini valid.
    jadwal = models.ForeignKey(JadwalKonselor, on_delete=models.CASCADE, null=True, blank=True)
    
    tanggal_sesi = models.DateTimeField(auto_now_add=True) 
    catatan_konselor = models.TextField(blank=True, null=True)
    total_biaya = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.total_biaya:
            if self.konselor:
                self.total_biaya = self.konselor.tarif_dasar + self.konselor.tarif_sesi
            else:
                self.total_biaya = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.pasien} - Rp {self.total_biaya:,.0f}"

# --- MODEL 4: PEMBAYARAN ---
class Pembayaran(models.Model):
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE)
    booking = models.OneToOneField(JadwalBooking, on_delete=models.CASCADE, related_name='pembayaran')
    jumlah = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=(("pending", "Pending"), ("paid", "Lunas")),
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pembayaran {self.pasien} - {self.status}"
    
