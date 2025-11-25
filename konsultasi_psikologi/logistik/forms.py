from django import forms
from .models import Inventori, Cabang, Supplier, BarangMasuk

class InventoriForm(forms.ModelForm):
    class Meta:
        model = Inventori
        fields = ['nama', 'kategori', 'stok', 'harga']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control'}),
            'stok': forms.NumberInput(attrs={'class': 'form-control'}),
            'harga': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CabangForm(forms.ModelForm):
    class Meta:
        model = Cabang
        fields = ['nama_cabang', 'alamat', 'kontak', 'manager']
        widgets = {
            'nama_cabang': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'kontak': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['nama_supplier', 'kategori', 'kontak']
        widgets = {
            'nama_supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control'}),
            'kontak': forms.TextInput(attrs={'class':'form-control'})
        }


class BarangMasukForm(forms.ModelForm):
    class Meta:
        model = BarangMasuk
        fields = ['supplier', 'inventori', 'jumlah',]
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'inventori': forms.Select(attrs={'class': 'form-control'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control'}),
            
        }
