from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Pasien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pasien_profile')
    nama = models.CharField(max_length=150)
    umur = models.PositiveIntegerField(null=True, blank=True)
    jenis_kelamin = models.CharField(max_length=20, blank=True)
    kontak = models.CharField(max_length=50, blank=True)
    alamat = models.TextField(blank=True)

    TINGKAT_CHOICES = [
        ('ringan', 'Ringan'),
        ('sedang', 'Sedang'),
        ('berat', 'Berat'),
    ]
    tingkat_gangguan = models.CharField(max_length=10, choices=TINGKAT_CHOICES, null=True, blank=True)
    sudah_isi_kuesioner = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nama} ({self.user.username})"


@receiver(post_save, sender=User)
def create_or_update_pasien_profile(sender, instance, created, **kwargs):
    if created:
        Pasien.objects.create(user=instance, nama=instance.username)
    else:
        instance.pasien_profile.save()


class Kuesioner(models.Model):
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, related_name='kuesioner')
    tanggal = models.DateTimeField(default=timezone.now)

    q1 = models.IntegerField(default=1)
    q2 = models.IntegerField(default=1)
    q3 = models.IntegerField(default=1)
    q4 = models.IntegerField(default=1)
    q5 = models.IntegerField(default=1)

    skor_total = models.IntegerField(default=0)
    hasil = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ['-tanggal']

    def save(self, *args, **kwargs):
        self.skor_total = (
            self.q1 + self.q2 + self.q3 + self.q4 + self.q5
        )

        if self.skor_total <= 12:
            self.hasil = 'ringan'
        elif self.skor_total <= 20:
            self.hasil = 'sedang'
        else:
            self.hasil = 'berat'

        super().save(*args, **kwargs)

        if self.pasien.tingkat_gangguan != self.hasil:
            self.pasien.tingkat_gangguan = self.hasil
            self.pasien.sudah_isi_kuesioner = True
            self.pasien.save()

    def __str__(self):
        return f"Kuesioner {self.pk} - {self.pasien.nama}"


class RiwayatKonsultasi(models.Model):
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, related_name='riwayat')
    tanggal = models.DateTimeField(default=timezone.now)
    konselor_nama = models.CharField(max_length=200, blank=True)
    ringkasan = models.TextField(blank=True)
    jenis_sesi = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-tanggal']

    def __str__(self):
        return f"Riwayat {self.pasien.nama} - {self.tanggal.date()}"


class BookingRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done'),
    ]

    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, related_name='bookings')
    konselor = models.ForeignKey('konsultasi.Konselor', on_delete=models.SET_NULL, null=True, blank=True)

    tanggal = models.DateField()
    jam_mulai = models.TimeField()
    durasi_menit = models.PositiveIntegerField(default=60)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.pasien.nama} @ {self.tanggal} {self.jam_mulai}"
