from django import forms
from .models import Resep, ResepItem, ObatOrder
from logistik.models import Inventori


# -------------------------------------------------------------
# Form Resep
# -------------------------------------------------------------
class ResepForm(forms.ModelForm):
    class Meta:
        model = Resep
        fields = ['konsultasi', 'pasien', 'konselor', 'catatan']
        widgets = {
            'catatan': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'form-control',
                    'placeholder': 'Catatan tambahan untuk resep...'
                }
            ),
        }


# -------------------------------------------------------------
# Form Item Resep
# -------------------------------------------------------------
class ResepItemForm(forms.ModelForm):

    # Pilihan obat dari Inventori
    inventori = forms.ModelChoiceField(
        queryset=Inventori.objects.all(),
        required=False,
        label="Pilih dari Inventori (Opsional)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ResepItem
        fields = ['inventori', 'dosis', 'jumlah']

        widgets = {
            'dosis': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Contoh: 2x sehari'
                }
            ),
            'jumlah': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'placeholder': 'Jumlah obat'
                }
            ),
        }


# -------------------------------------------------------------
# Form Order Obat
# -------------------------------------------------------------
class ObatOrderForm(forms.ModelForm):
    class Meta:
        model = ObatOrder
        fields = ['metode', 'alamat_pengiriman', 'jasa_pengiriman', 'biaya_kurir']

        widgets = {
            'metode': forms.Select(attrs={'class': 'form-select'}),
            'alamat_pengiriman': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Alamat lengkap tujuan pengiriman...'
                }
            ),
            'jasa_pengiriman': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Contoh: JNE, J&T, SiCepat'
                }
            ),
            'biaya_kurir': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0
                }
            ),
        }
