from django import forms
from .models import Resep, ResepItem, ObatOrder
from logistik.models import Inventori

class ResepForm(forms.ModelForm):
    class Meta:
        model = Resep
        fields = ['konsultasi', 'pasien', 'konselor', 'catatan']
        widgets = {
            'catatan': forms.Textarea(attrs={'rows':3}),
        }

class ResepItemForm(forms.ModelForm):
    # tampilkan inventori sebagai dropdown
    inventori = forms.ModelChoiceField(queryset=Inventori.objects.all(), required=False, label="Pilih dari Inventori (opsional)")

    class Meta:
        model = ResepItem
        fields = ['inventori', 'dosis', 'jumlah']
        # nama_obat & harga_satuan diisi otomatis dari inventori

class ObatOrderForm(forms.ModelForm):
    class Meta:
        model = ObatOrder
        fields = ['metode', 'alamat_pengiriman', 'jasa_pengiriman', 'biaya_kurir']
