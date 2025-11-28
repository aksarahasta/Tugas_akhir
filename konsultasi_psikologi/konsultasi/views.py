from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
# Import model yang SUDAH DIPERBAIKI namanya
from .models import Konselor, JadwalKonselor, JadwalBooking, Pembayaran
from django.db.models import Sum
from .forms import KonselorForm, JadwalForm, SesiKonsultasiForm, PembayaranKonsultasiForm


# =============================
# CRUD KONSELOR
# =============================
def konselor_list(request):
    data = Konselor.objects.all()
    return render(request, 'konsultasi/konselor_list.html', {'konselors': data})

def konselor_add(request):
    form = KonselorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Data Konselor ditambahkan.")
        return redirect('konselor_list')
    return render(request, 'konsultasi/konselor_form.html', {'form': form, 'judul': 'Tambah Konselor'})

def konselor_edit(request, pk):
    k = get_object_or_404(Konselor, pk=pk)
    form = KonselorForm(request.POST or None, instance=k)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Data Konselor diperbarui.")
        return redirect('konselor_list')
    return render(request, 'konsultasi/konselor_form.html', {'form': form, 'judul': 'Edit Konselor'})

def konselor_delete(request, pk):
    k = get_object_or_404(Konselor, pk=pk)
    k.delete()
    messages.info(request, "Konselor dihapus.")
    return redirect('konselor_list')

# =============================
# CRUD JADWAL
# =============================
def jadwal_list(request):
    data = JadwalKonselor.objects.select_related('konselor').all()
    return render(request, 'konsultasi/jadwal_list.html', {'jadwal': data})

def jadwal_add(request):
    form = JadwalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Jadwal ditambahkan.")
        return redirect('jadwal_list')
    return render(request, 'konsultasi/jadwal_form.html', {'form': form, 'judul': 'Tambah Jadwal'})

def jadwal_edit(request, pk):
    j = get_object_or_404(JadwalKonselor, pk=pk)
    form = JadwalForm(request.POST or None, instance=j)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Jadwal diperbarui.")
        return redirect('jadwal_list')
    return render(request, 'konsultasi/jadwal_form.html', {'form': form, 'judul': 'Edit Jadwal'})

def jadwal_delete(request, pk):
    j = get_object_or_404(JadwalKonselor, pk=pk)
    j.delete()
    messages.info(request, "Jadwal dihapus.")
    return redirect('jadwal_list')

# =============================
# SESI & PEMBAYARAN
# =============================
def sesi_list(request):
    # Saya tambahkan 'jadwal' di select_related biar tanggal & jam langsung ke-load
    data = JadwalBooking.objects.select_related('pasien', 'konselor', 'jadwal').all()
    return render(request, 'konsultasi/sesi_list.html', {'booking': data})

def pembayaran_list(request):
    data = Pembayaran.objects.select_related('booking').all()
    return render(request, 'konsultasi/pembayaran_list.html', {'data': data})


def daftar_pembayaran(request):
    pembayaran_list = Pembayaran.objects.all().select_related('pasien', 'booking').order_by('-created_at')

    # Perhatikan 'jumlah' harus sesuai dengan nama field di models.py Anda
    agregat = pembayaran_list.filter(status='paid').aggregate(Sum('jumlah'))
    total_sum = agregat['jumlah_sum']
    
    # Jika None (belum ada data), set jadi 0
    total_pendapatan = total_sum if total_sum is not None else 0

    context = {
        'pembayaran_list': pembayaran_list,
        'total_pendapatan': total_pendapatan,
        'title': 'Data Pembayaran Konsultasi'
    }
    return render(request, 'konsultasi/pembayaran_list.html', context)