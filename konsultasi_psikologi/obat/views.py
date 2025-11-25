from django.shortcuts import render

# Create your views here.
# obat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from .models import Resep, ResepItem, ObatOrder
from .forms import ResepForm, ResepItemForm, ObatOrderForm
from logistik.models import Inventori
from pasien.models import Pasien

def resep_list(request):
    qs = Resep.objects.select_related('pasien','konselor').order_by('-tanggal')
    return render(request, 'obat/resep_list.html', {'resep_qs': qs})

def resep_add(request):
    if request.method == 'POST':
        form = ResepForm(request.POST)
        if form.is_valid():
            r = form.save()
            messages.success(request, "Resep berhasil dibuat. Silakan tambah item obat.")
            return redirect('resep_edit', pk=r.pk)
    else:
        form = ResepForm()
    return render(request, 'obat/resep_form.html', {'form': form, 'judul': 'Buat Resep'})

def resep_edit(request, pk):
    r = get_object_or_404(Resep, pk=pk)
    item_form = ResepItemForm()
    if request.method == 'POST' and 'add_item' in request.POST:
        item_form = ResepItemForm(request.POST)
        if item_form.is_valid():
            it = item_form.save(commit=False)
            it.resep = r
            # jika inventori dipilih, ResepItem.save() akan otomatis mengisi nama & harga
            it.save()
            messages.success(request, "Item obat ditambahkan.")
            return redirect('resep_edit', pk=r.pk)
    items = r.items.select_related('inventori').all()
    return render(request, 'obat/resep_edit.html', {'r': r, 'items': items, 'item_form': item_form})

def resep_item_delete(request, pk_item):
    it = get_object_or_404(ResepItem, pk=pk_item)
    resep_pk = it.resep.pk
    it.delete()
    messages.info(request, "Item resep dihapus.")
    return redirect('resep_edit', pk=resep_pk)


def order_from_resep(request, resep_id):
    r = get_object_or_404(Resep, pk=resep_id)
    if request.method == 'POST':
        form = ObatOrderForm(request.POST)
        if form.is_valid():
            o = form.save(commit=False)
            o.resep = r
            o.pasien = r.pasien
            o.save()  # recalc totals
            messages.success(request, f"Order berhasil dibuat. Total: {o.total:.2f}")
            return redirect('order_detail', pk=o.pk)
    else:
        form = ObatOrderForm(initial={'metode':'ambil'})
    return render(request, 'obat/order_form.html', {'form': form, 'resep': r})


def order_list(request):
    qs = ObatOrder.objects.select_related('resep','pasien').order_by('-tanggal_order')
    return render(request, 'obat/order_list.html', {'orders': qs})


def order_detail(request, pk):
    o = get_object_or_404(ObatOrder, pk=pk)
    if request.method == 'POST' and 'set_status' in request.POST:
        new_status = request.POST.get('status')
        allowed = ['diproses','dikirim','selesai','batal']
        if new_status not in allowed:
            messages.error(request, "Status tidak valid.")
            return redirect('order_detail', pk=o.pk)

        with transaction.atomic():
            prev_status = o.status
            o.status = new_status
            o.save()
            # jika berubah menjadi 'dikirim' atau 'selesai' -> kurangi stok inventori
            if new_status in ('dikirim','selesai'):
                for it in o.resep.items.select_related('inventori').all():
                    inv = it.inventori
                    if inv:
                        # gunakan atribut stok umum
                        stok_field_candidates = ['jumlah_stok','stok','quantity']
                        stok_val = None
                        if hasattr(inv, 'jumlah_stok'):
                            stok_val = getattr(inv, 'jumlah_stok')
                        elif hasattr(inv, 'stok'):
                            stok_val = getattr(inv, 'stok')
                        elif hasattr(inv, 'quantity'):
                            stok_val = getattr(inv, 'quantity')

                        if stok_val is None:
                            # tidak ada field stok -> lewati (log/alert)
                            # butuh perbaikan pada model Inventori
                            continue

                        # pastikan stok tidak negatif
                        new_stok = max(0, stok_val - it.jumlah)
                        # simpan pada properti yang sesuai
                        if hasattr(inv, 'jumlah_stok'):
                            inv.jumlah_stok = new_stok
                        elif hasattr(inv, 'stok'):
                            inv.stok = new_stok
                        elif hasattr(inv, 'quantity'):
                            inv.quantity = new_stok
                        inv.save()
            messages.success(request, f"Status order diubah ke {new_status}.")
            return redirect('order_detail', pk=o.pk)

    return render(request, 'obat/order_detail.html', {'order': o})
