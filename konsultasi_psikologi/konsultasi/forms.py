from django import forms
from .models import Konselor, JadwalKonselor, JadwalBooking, Pembayaran

class KonselorForm(forms.ModelForm):
    class Meta:
        model = Konselor
        # Pastikan field ini ada di models.py
        fields = ['nama', 'no_hp', 'spesialisasi', 'tarif_dasar', 'tarif_sesi']

class JadwalForm(forms.ModelForm):
    # Field 'hari' kita definisikan manual di sini
    hari = forms.MultipleChoiceField(
        choices=[
            ('Senin', 'Senin'),
            ('Selasa', 'Selasa'),
            ('Rabu', 'Rabu'),
            ('Kamis', 'Kamis'),
            ('Jumat', 'Jumat'),
            ('Sabtu', 'Sabtu'),
            ('Minggu', 'Minggu'),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Pilih Hari Praktek (Bisa lebih dari satu)"
    )

    class Meta:
        model = JadwalKonselor
        # PERBAIKAN PENTING DI SINI:
        # Hapus 'hari' dari daftar fields di bawah ini
        # Agar Django tidak memvalidasinya sebagai single value
        fields = ['konselor', 'jam_mulai', 'jam_selesai', 'fokus']
        
        widgets = {
            'konselor': forms.Select(attrs={'class': 'form-select'}),
            'jam_mulai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'jam_selesai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fokus': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        if not commit:
            return super().save(commit=False)

        # Ambil data hari dari form manual
        hari_list = self.cleaned_data.get('hari')
        
        # Ambil data lain dari ModelForm dasar
        instance = super().save(commit=False)
        
        first_obj = None

        # Kita buat object JadwalKonselor satu per satu untuk setiap hari
        for h in hari_list:
            obj = JadwalKonselor(
                konselor=instance.konselor,
                hari=h, # Set hari di sini
                jam_mulai=instance.jam_mulai,
                jam_selesai=instance.jam_selesai,
                fokus=instance.fokus
            )
            obj.save()
            if first_obj is None:
                first_obj = obj
        
        return first_obj


class SesiKonsultasiForm(forms.ModelForm):
    class Meta:
        model = JadwalBooking
        # Kita sesuaikan field dengan model JadwalBooking
        fields = ['pasien', 'konselor', 'jadwal', 'catatan_konselor', 'status']

class PembayaranKonsultasiForm(forms.ModelForm):
    class Meta:
        model = Pembayaran
        fields = ['booking', 'jumlah', 'status']

class UploadBuktiPembayaranForm(forms.ModelForm):
    class Meta:
        model = Pembayaran
        fields = ['bukti_pembayaran']
        widgets = {
            'bukti_pembayaran': forms.ClearableFileInput(attrs={
                'accept': 'image/*,.pdf',
                'class': 'form-control-file'
            })
        }
    
