from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
# Import model yang SUDAH DIPERBAIKI namanya
from .models import Konselor, JadwalKonselor, JadwalBooking, Pembayaran
from django.db.models import Sum, Count
from .forms import KonselorForm, JadwalForm, SesiKonsultasiForm, PembayaranKonsultasiForm, UploadBuktiPembayaranForm
import json
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models.functions import TruncDate    

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
    # MENAMBAHKAN FITUR SORTIR TANGGAL
    sort_by = request.GET.get('sort', 'baru')
    
    if sort_by == 'lama':
        order = 'tanggal_sesi'  # Urutkan dari tanggal lama ke baru
    else:
        order = '-tanggal_sesi' # Urutkan dari tanggal baru ke lama (Default)

    # Mengambil data dengan urutan yang dipilih
    data = JadwalBooking.objects.select_related('pasien', 'konselor', 'jadwal').order_by(order)
    
    return render(request, 'konsultasi/sesi_list.html', {
        'booking': data,
        'current_sort': sort_by # Digunakan untuk menandai tombol aktif di HTML
    })

def sesi_detail(request, pk):
    # Ambil data sesi berdasarkan ID
    sesi = get_object_or_404(JadwalBooking, pk=pk)
    
    context = {
        'sesi': sesi,
        'title': 'Detail Sesi Konsultasi'
    }
    return render(request, 'konsultasi/sesi_detail.html', context)

def pembayaran_list(request):
    data = Pembayaran.objects.select_related('booking').all()
    return render(request, 'konsultasi/pembayaran_list.html', {'data': data})


@login_required

def upload_bukti_pembayaran(request, payment_id):
    """View for patients to upload payment proof"""
    pembayaran = get_object_or_404(Pembayaran, id=payment_id)
    
    # Authorization check - patient can only upload for their own payments
    if request.user != pembayaran.pasien.user:
        messages.error(request, "Akses ditolak.")
        return redirect('dashboard')
    
    # Check if payment is eligible for upload
    if pembayaran.status not in ['pending', 'rejected']:
        messages.warning(request, "Pembayaran ini tidak dapat diunggah bukti.")
        return redirect('payment_detail', payment_id=payment_id)
    
    if request.method == 'POST':
        form = UploadBuktiPembayaranForm(request.POST, request.FILES, instance=pembayaran)
        if form.is_valid():
            with transaction.atomic():  # NEW: Transaction for safety
                pembayaran = form.save(commit=False)
                pembayaran.status = 'uploaded'  # NEW: Change status
                pembayaran.tanggal_upload = timezone.now()  # NEW: Set timestamp
                pembayaran.save()
                
                # NEW: Update booking status
                if pembayaran.booking.status == 'confirmed':
                    pembayaran.booking.status = 'waiting_payment_verification'
                    pembayaran.booking.save()
                     messages.success(request, "Bukti pembayaran berhasil diunggah! Menunggu verifikasi admin.")
            return redirect('payment_detail', payment_id=pembayaran.id)
    else:
        form = UploadBuktiPembayaranForm(instance=pembayaran)
    
    return render(request, 'payments/upload_bukti.html', {
        'form': form,
        'pembayaran': pembayaran,
        'title': 'Upload Bukti Pembayaran'
    })

@login_required
def payment_detail(request, payment_id):
    """View payment details"""
    pembayaran = get_object_or_404(Pembayaran, id=payment_id)
    
    # Authorization: patient sees their own, staff sees all
    if request.user != pembayaran.pasien.user and not request.user.is_staff:
        messages.error(request, "Akses ditolak.")
        return redirect('home')
    
    # NEW: Check if patient can upload proof
    can_upload = pembayaran.status in ['pending', 'rejected']
    
    return render(request, 'payments/payment_detail.html', {
        'pembayaran': pembayaran,
        'can_upload': can_upload,  # NEW: Pass this to template
        'title': 'Detail Pembayaran'
    })

@login_required
def daftar_pembayaran(request):
    # 1. Base Query (Ambil semua data pembayaran yang sudah lunas/paid)
    # Kita filter status='paid' di awal agar perhitungan uang valid
    qs = Pembayaran.objects.filter(status='paid').select_related('pasien', 'booking')
    
    # 2. Perhitungan Statistik Waktu
    now = timezone.now()
    
    # Pendapatan Hari Ini
    income_today = qs.filter(created_at__date=now.date()).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    
    # Pendapatan Bulan Ini
    income_month = qs.filter(created_at__month=now.month, created_at__year=now.year).aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    
    # Total Pendapatan Seumur Hidup
    income_total = qs.aggregate(Sum('jumlah'))['jumlah__sum'] or 0

    # 3. Data Grafik (7 Hari Terakhir)
    # Mengelompokkan pendapatan berdasarkan tanggal
    last_7_days = qs.filter(created_at__gte=now - timezone.timedelta(days=7)) \
                    .annotate(date=TruncDate('created_at')) \
                    .values('date') \
                    .annotate(total=Sum('jumlah')) \
                    .order_by('date')
    
    # Format data untuk dikirim ke Javascript (ApexCharts)
    graph_dates = [item['date'].strftime('%d %b') for item in last_7_days]
    graph_values = [int(item['total']) for item in last_7_days]

    # 4. Rekap Per Konselor (Top 5)
    # Asumsi: booking punya relasi ke konselor
    counselor_stats = qs.values('booking__konselor__nama') \
                        .annotate(total_pendapatan=Sum('jumlah'), jumlah_transaksi=Count('id')) \
                        .order_by('-total_pendapatan')[:5]

    # 5. List Tabel (Semua data, termasuk pending, untuk tabel riwayat)
    # Khusus tabel, kita ambil semua status (pending/cancel) juga biar admin tau
    all_transactions = Pembayaran.objects.all().select_related('pasien', 'booking').order_by('-created_at')

    context = {
        'title': 'Keuangan & Pembayaran',
        'pembayaran_list': all_transactions,
        'income_today': income_today,
        'income_month': income_month,
        'income_total': income_total,
        'counselor_stats': counselor_stats,
        # Kirim data grafik sebagai JSON string aman
        'graph_dates': json.dumps(graph_dates),
        'graph_values': json.dumps(graph_values),
    }
    
    return render(request, 'konsultasi/pembayaran_list.html', context)

def pembayaran_detail(request, pk):
    # Mengambil data pembayaran berdasarkan ID (pk), atau tampilkan error 404 jika tidak ada
    # select_related digunakan untuk optimasi query (mengambil data pasien & booking sekaligus)
    pembayaran = get_object_or_404(Pembayaran.objects.select_related('pasien', 'booking'), pk=pk)
    
    context = {
        'pembayaran': pembayaran,
        'title': f'Detail Pembayaran #{pembayaran.id}'
    }
    return render(request, 'konsultasi/pembayaran_detail.html', context)
