from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Inventori, Cabang, Supplier, BarangMasuk
from .forms import InventoriForm, CabangForm, SupplierForm, BarangMasukForm

# INVENTORI

def inventori_list(request):
    inventori = Inventori.objects.all().order_by('kategori', 'nama')
    return render(request, 'logistik/inventori_list.html', {'inventori': inventori})


def inventori_tambah(request):
    if request.method == 'POST':
        form = InventoriForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data inventori ditambahkan.')
            return redirect('inventori_list')
    else:
        form = InventoriForm()
    return render(request, 'logistik/inventori_form.html', {'form': form, 'judul': 'Tambah Inventori'})


def inventori_edit(request, pk):
    item = get_object_or_404(Inventori, pk=pk)
    if request.method == 'POST':
        form = InventoriForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data inventori diperbarui.')
            return redirect('inventori_list')
    else:
        form = InventoriForm(instance=item)
    return render(request, 'logistik/inventori_form.html', {'form': form, 'judul': 'Edit Inventori'})


def inventori_hapus(request, pk):
    item = get_object_or_404(Inventori, pk=pk)
    item.delete()
    messages.info(request, 'Data inventori dihapus.')
    return redirect('inventori_list')

# CABANG

def cabang_list(request):
    cabang = Cabang.objects.all()
    return render(request, 'logistik/cabang_list.html', {'cabang': cabang})


def cabang_tambah(request):
    if request.method == 'POST':
        form = CabangForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cabang ditambahkan.')
            return redirect('cabang_list')
    else:
        form = CabangForm()
    return render(request, 'logistik/cabang_form.html', {'form': form, 'judul': 'Tambah Cabang'})


def cabang_edit(request, pk):
    cb = get_object_or_404(Cabang, pk=pk)
    if request.method == 'POST':
        form = CabangForm(request.POST, instance=cb)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data cabang diperbarui.')
            return redirect('cabang_list')
    else:
        form = CabangForm(instance=cb)
    return render(request, 'logistik/cabang_form.html', {'form': form, 'judul': 'Edit Cabang'})


def cabang_hapus(request, pk):
    cb = get_object_or_404(Cabang, pk=pk)
    cb.delete()
    messages.info(request, 'Cabang dihapus.')
    return redirect('cabang_list')


# SUPPLIER

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'logistik/supplier_list.html', {'suppliers': suppliers})


def supplier_tambah(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier ditambahkan.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'logistik/supplier_form.html', {'form': form, 'judul': 'Tambah Supplier'})


def supplier_edit(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier diperbarui.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=s)
    return render(request, 'logistik/supplier_form.html', {'form': form, 'judul': 'Edit Supplier'})


def supplier_hapus(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    s.delete()
    messages.info(request, 'Supplier dihapus.')
    return redirect('supplier_list')


# BARANG MASUK

def barangmasuk_list(request):
    barang_masuk = BarangMasuk.objects.all().order_by('-tanggal')
    return render(request, 'logistik/barangmasuk_list.html', {'barang_masuk': barang_masuk})


def barangmasuk_tambah(request):
    if request.method == 'POST':
        form = BarangMasukForm(request.POST)
        if form.is_valid():
            bm = form.save(commit=False)
            # update stok inventori
            bm.inventori.stok += bm.jumlah
            bm.inventori.save()
            bm.save()
            messages.success(request, 'Barang masuk dicatat dan stok bertambah.')
            return redirect('barangmasuk_list')
    else:
        form = BarangMasukForm()
    return render(request, 'logistik/barangmasuk_form.html', {'form': form, 'judul': 'Tambah Barang Masuk'})
