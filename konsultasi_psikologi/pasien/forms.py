from django import forms
from django.contrib.auth.models import User
from .models import Pasien, Kuesioner
# Kita import model dari aplikasi konsultasi
from konsultasi.models import JadwalBooking, JadwalKonselor, Pembayaran

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Ulangi Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Password tidak sama.")
        return cleaned

class PasienForm(forms.ModelForm):
    class Meta:
        model = Pasien
        fields = ['nama', 'umur', 'jenis_kelamin', 'kontak', 'alamat']

class KuesionerForm(forms.ModelForm):
    class Meta:
        model = Kuesioner
        fields = ['q1','q2','q3','q4','q5']
        widgets = {
            'q1': forms.NumberInput(attrs={'min':1,'max':5}),
            'q2': forms.NumberInput(attrs={'min':1,'max':5}),
            'q3': forms.NumberInput(attrs={'min':1,'max':5}),
            'q4': forms.NumberInput(attrs={'min':1,'max':5}),
            'q5': forms.NumberInput(attrs={'min':1,'max':5}),
        }

# --- FORM BOOKING: DIFOKUSKAN PADA TANGGAL & PENCEGAHAN BENTROK ---
class BookingForm(forms.ModelForm):
    # Pasien memilih jadwal yang SUDAH DIBUAT konselor
    jadwal = forms.ModelChoiceField(
        queryset=JadwalKonselor.objects.filter(is_booked=False), 
        label="Pilih Jam Tersedia",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = JadwalBooking
        # Menambahkan 'tanggal_sesi' agar pasien bisa memilih tanggal konsultasi
        fields = ['tanggal_sesi', 'konselor', 'jadwal'] 
        labels = {
            'tanggal_sesi': 'Pilih Tanggal Konsultasi',
            'konselor': 'Pilih Konselor',
        }
        widgets = {
            # Menggunakan type='date' agar browser memunculkan kalender
            'tanggal_sesi': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'konselor': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tanggal = cleaned_data.get('tanggal_sesi')
        konselor = cleaned_data.get('konselor')
        jadwal = cleaned_data.get('jadwal')

        # Logika Pencegahan Double Booking:
        # Mengecek apakah kombinasi Tanggal, Konselor, dan Jam sudah ada di database
        if tanggal and konselor and jadwal:
            bentrok = JadwalBooking.objects.filter(
                tanggal_sesi=tanggal,
                konselor=konselor,
                jadwal=jadwal,
                status__in=['pending', 'terjadwal']
            ).exists()

            if bentrok:
                # Memberikan pesan error jika jadwal sudah diambil
                raise forms.ValidationError(
                    f"Maaf, konselor {konselor.nama} sudah dipesan pada tanggal {tanggal} di jam tersebut. Silakan pilih waktu atau tanggal lain."
                )
        
        return cleaned_data

# --- FORM UNTUK PEMBAYARAN PASIEN (KEMBALI KE KODE AWAL ANDA) ---
class PembayaranForm(forms.ModelForm):
    class Meta:
        model = Pembayaran
        fields = []