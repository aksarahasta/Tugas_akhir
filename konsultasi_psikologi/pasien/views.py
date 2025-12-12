from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, PasienForm, KuesionerForm, BookingForm
from konsultasi.models import JadwalBooking, Pembayaran

from .models import Pasien, Kuesioner, RiwayatKonsultasi, BookingRequest
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        pasien_form = PasienForm(request.POST)
        
        if user_form.is_valid() and pasien_form.is_valid():
            # 1. Buat User
            # (Saat baris ini jalan, Signal di models.py OTOMATIS membuat Pasien kosong)
            user = User.objects.create_user(
                username=user_form.cleaned_data['username'],
                email=user_form.cleaned_data.get('email'),
                password=user_form.cleaned_data['password']
            )

            # 2. Ambil Pasien yang sudah dibuat oleh Signal tadi
            # Kita akses pakai related_name 'pasien_profile' (pastikan sama dengan di models.py)
            try:
                pasien = user.pasien_profile
                
                # 3. Update data Pasien tersebut dengan data dari Form
                pasien.nama = pasien_form.cleaned_data.get('nama')
                pasien.umur = pasien_form.cleaned_data.get('umur')
                pasien.jenis_kelamin = pasien_form.cleaned_data.get('jenis_kelamin')
                pasien.kontak = pasien_form.cleaned_data.get('kontak')
                pasien.alamat = pasien_form.cleaned_data.get('alamat')
                
                # Simpan perubahan
                pasien.save()

                # 4. Login user otomatis & Redirect
                login(request, user)
                messages.success(request, "Akun berhasil dibuat. Silakan isi kuesioner.")
                return redirect('kuesioner_isi')
            
            except AttributeError:
                # Fallback jika signal tidak jalan / related_name salah
                messages.error(request, "Terjadi kesalahan sistem: Profil pasien tidak terbentuk otomatis.")
                # Hapus user agar tidak jadi sampah
                user.delete()
            
    else:
        user_form = UserRegisterForm()
        pasien_form = PasienForm()
    
    # Render template dengan dua form context
    return render(request, 'pasien/register.html', {
        'user_form': user_form, 
        'pasien_form': pasien_form
    })

# --- Di bawah ini biarkan saja sama seperti sebelumnya ---

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        user = authenticate(request, username=username, password=pwd)
        if user:
            login(request, user)
            messages.success(request, "Login berhasil")
            return redirect('dashboard')
        messages.error(request, "Login gagal: cek username/password")
    return render(request, 'pasien/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Anda logout.")
    return redirect('login')

@login_required
def dashboard(request):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    last_kues = None
    bookings = []
    if pasien_profile:
        last_kues = pasien_profile.kuesioner.order_by('-tanggal').first()
        bookings = pasien_profile.bookings.order_by('-created_at')[:5]
    return render(request, 'pasien/dashboard.html', {'pasien_profile': pasien_profile, 'last_kues': last_kues, 'bookings': bookings})

# PASIEN CRUD
@login_required
def pasien_list(request):
    pasien_all = Pasien.objects.all().order_by('-created_at')
    return render(request, 'pasien/pasien_list.html', {'data': pasien_all})

@login_required
def pasien_detail(request, pk):
    p = get_object_or_404(Pasien, pk=pk)
    kues = p.kuesioner.all().order_by('-tanggal')
    # Menggunakan 'riwayat' karena related_name di models
    riwayat = p.riwayat.all().order_by('-tanggal') 
    bookings = p.bookings.all().order_by('-created_at')
    return render(request, 'pasien/pasien_detail.html', {'p': p, 'kuesioner': kues, 'riwayat': riwayat, 'bookings': bookings})

@login_required
def pasien_edit(request, pk):
    p = get_object_or_404(Pasien, pk=pk)
    if request.method == 'POST':
        form = PasienForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil pasien diperbarui.")
            return redirect('pasien_detail', pk=p.pk)
    else:
        form = PasienForm(instance=p)
    return render(request, 'pasien/pasien_form.html', {'form': form, 'judul': 'Edit Pasien'})

# KUESIONER
@login_required
def kuesioner_isi(request):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    if not pasien_profile:
        messages.error(request, "Tidak ada profil pasien untuk user ini.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = KuesionerForm(request.POST)
        if form.is_valid():
            k = form.save(commit=False)
            k.pasien = pasien_profile
            k.save()
            messages.success(request, "Kuesioner tersimpan. Hasil: %s (skor %d)" % (k.hasil, k.skor_total))
            return redirect('dashboard')
    else:
        form = KuesionerForm()
    return render(request, 'pasien/kuesioner_form.html', {'form': form})

@login_required
def kuesioner_list(request):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    if not pasien_profile:
        messages.error(request, "Profil pasien tidak ditemukan.")
        return redirect('dashboard')
    data = Kuesioner.objects.filter(pasien=pasien_profile).order_by('-tanggal')
    return render(request, 'pasien/kuesioner_list.html', {'data': data})

# BOOKING

@login_required
def booking_create(request):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    if not pasien_profile:
        messages.error(request, "Profil pasien tidak ditemukan.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # 1. Simpan Booking
            booking = form.save(commit=False)
            booking.pasien = pasien_profile
            booking.status = 'pending'
            booking.save()
            
            messages.success(request, "Jadwal berhasil dipilih. Silakan selesaikan pembayaran.")
            
            # --- PERBAIKAN ALUR DI SINI ---
            # Jangan ke dashboard, tapi langsung ke halaman BAYAR
            return redirect('booking_pay', booking_id=booking.id)
            
    else:
        form = BookingForm()
    
    return render(request, 'pasien/booking_form.html', {'form': form})
    

@login_required
def booking_list(request):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    if not pasien_profile:
        return redirect('dashboard')
    
    # Ambil semua booking milik pasien ini (gunakan related_name 'jadwal_bookings')
    bookings = pasien_profile.jadwal_bookings.select_related('konselor', 'jadwal').order_by('-tanggal_sesi')
    
    return render(request, 'pasien/booking_list.html', {'bookings': bookings})

@login_required
def booking_pay(request, booking_id):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    
    # Ambil booking yang spesifik, pastikan milik pasien ini
    booking = get_object_or_404(JadwalBooking, id=booking_id, pasien=pasien_profile)
    
    if booking.is_paid:
        messages.info(request, "Booking ini sudah lunas.")
        return redirect('booking_list')

    if request.method == 'POST':
        # 1. Buat data Pembayaran
        Pembayaran.objects.create(
            pasien=pasien_profile,
            booking=booking,
            jumlah=booking.total_biaya, # Bayar sesuai tagihan
            status='paid'
        )
        
        # 2. Update status Booking jadi Lunas & Terjadwal
        booking.is_paid = True
        booking.status = 'terjadwal'
        booking.save()
        
        messages.success(request, "Pembayaran berhasil! Jadwal Anda telah dikonfirmasi.")
        return redirect('booking_list')
        
    return render(request, 'pasien/booking_pay.html', {'booking': booking})
