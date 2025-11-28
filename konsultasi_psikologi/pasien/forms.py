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

# --- FORM BARU UNTUK BOOKING ---
class BookingForm(forms.ModelForm):
    # Pasien memilih jadwal yang SUDAH DIBUAT konselor
    jadwal = forms.ModelChoiceField(
        queryset=JadwalKonselor.objects.filter(is_booked=False), # Hanya tampilkan yg belum dibooking
        label="Pilih Jadwal Tersedia",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = JadwalBooking
        fields = ['konselor', 'jadwal'] # Pasien pilih konselor & jadwalnya
        widgets = {
            'konselor': forms.Select(attrs={'class': 'form-select'}),
        }

# --- FORM UNTUK PEMBAYARAN PASIEN ---
class PembayaranForm(forms.ModelForm):
    class Meta:
        model = Pembayaran
        # Field ini biasanya diisi otomatis di view, tapi kita bisa tampilkan 'jumlah' sebagai readonly di HTML nanti
        fields = [] 
        # Kita kosongkan fields karena Pasien hanya perlu klik "Konfirmasi Bayar"
        # Data jumlah dan booking akan di-set otomatis di views.py