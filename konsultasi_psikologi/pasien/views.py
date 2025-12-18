from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse 
from datetime import datetime 

from .forms import UserRegisterForm, PasienForm, KuesionerForm, BookingForm
from konsultasi.models import JadwalBooking, Pembayaran, JadwalKonselor 

from .models import Pasien, Kuesioner, RiwayatKonsultasi, BookingRequest
from django.contrib.auth.models import User

# --- FUNGSI AJAX: FILTER JADWAL BERDASARKAN HARI ---
def get_jadwal_opt(request):
    tanggal_str = request.GET.get('tanggal')
    konselor_id = request.GET.get('konselor_id')
    
    if tanggal_str and konselor_id:
        try:
            date_obj = datetime.strptime(tanggal_str, '%Y-%m-%d')
            hari_map = {
                0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis',
                4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'
            }
            nama_hari = hari_map[date_obj.weekday()]

            jadwals = JadwalKonselor.objects.filter(
                konselor_id=konselor_id, 
                hari=nama_hari, 
                is_booked=False
            )

            data = [
                {
                    'id': j.id, 
                    'jam': f"{j.konselor.nama} - ({j.jam_mulai.strftime('%H:%M')} s/d {j.jam_selesai.strftime('%H:%M')})"
                } 
                for j in jadwals
            ]
            return JsonResponse({'jadwals': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'jadwals': []})

# --- FUNGSI AUTH & CRUD ---

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        pasien_form = PasienForm(request.POST)
        
        if user_form.is_valid() and pasien_form.is_valid():
            user = User.objects.create_user(
                username=user_form.cleaned_data['username'],
                email=user_form.cleaned_data.get('email'),
                password=user_form.cleaned_data['password']
            )

            try:
                pasien = user.pasien_profile
                pasien.nama = pasien_form.cleaned_data.get('nama')
                pasien.umur = pasien_form.cleaned_data.get('umur')
                pasien.jenis_kelamin = pasien_form.cleaned_data.get('jenis_kelamin')
                pasien.kontak = pasien_form.cleaned_data.get('kontak')
                pasien.alamat = pasien_form.cleaned_data.get('alamat')
                pasien.save()

                login(request, user)
                messages.success(request, "Akun berhasil dibuat. Silakan isi kuesioner.")
                return redirect('kuesioner_isi')
            
            except AttributeError:
                messages.error(request, "Terjadi kesalahan sistem: Profil pasien tidak terbentuk otomatis.")
                user.delete()
            
    else:
        user_form = UserRegisterForm()
        pasien_form = PasienForm()
    
    return render(request, 'pasien/register.html', {
        'user_form': user_form, 
        'pasien_form': pasien_form
    })

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
        bookings = pasien_profile.jadwal_bookings.order_by('-tanggal_sesi')[:5]
    return render(request, 'pasien/dashboard.html', {'pasien_profile': pasien_profile, 'last_kues': last_kues, 'bookings': bookings})

@login_required
def pasien_list(request):
    pasien_all = Pasien.objects.all().order_by('-created_at')
    return render(request, 'pasien/pasien_list.html', {'data': pasien_all})

@login_required
def pasien_detail(request, pk):
    p = get_object_or_404(Pasien, pk=pk)
    kues = p.kuesioner.all().order_by('-tanggal')
    riwayat = p.riwayat.all().order_by('-tanggal') 
    bookings = p.jadwal_bookings.all().order_by('-tanggal_sesi')
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

# --- FITUR BOOKING & SORTIR TANGGAL ---

@login_required
def booking_create(request):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    if not pasien_profile:
        messages.error(request, "Profil pasien tidak ditemukan.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.pasien = pasien_profile
            booking.status = 'pending'
            booking.save()
            
            messages.success(request, "Jadwal berhasil dipilih. Silakan selesaikan pembayaran.")
            return redirect('booking_pay', booking_id=booking.id)
        else:
            messages.error(request, "Pilihan jadwal tidak tersedia. Silakan cek kembali.")
    else:
        form = BookingForm()
    
    return render(request, 'pasien/booking_form.html', {'form': form})

@login_required
def booking_list(request):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    if not pasien_profile:
        return redirect('dashboard')
    
    # Pengurutan berdasarkan parameter URL ?sort=
    sort_by = request.GET.get('sort', 'baru')
    if sort_by == 'lama':
        order = 'tanggal_sesi'  # Dari tanggal lama ke baru
    else:
        order = '-tanggal_sesi' # Dari tanggal baru ke lama (Default)

    # Mengambil jadwal_bookings milik pasien dengan urutan yang dipilih
    bookings = pasien_profile.jadwal_bookings.select_related('konselor', 'jadwal').order_by(order)
    
    return render(request, 'pasien/booking_list.html', {
        'bookings': bookings,
        'current_sort': sort_by 
    })

@login_required
def booking_pay(request, booking_id):
    pasien_profile = getattr(request.user, 'pasien_profile', None)
    booking = get_object_or_404(JadwalBooking, id=booking_id, pasien=pasien_profile)
    
    if booking.is_paid:
        messages.info(request, "Booking ini sudah lunas.")
        return redirect('booking_list')

    if request.method == 'POST':
        Pembayaran.objects.create(
            pasien=pasien_profile,
            booking=booking,
            jumlah=booking.total_biaya,
            status='paid'
        )
        
        booking.is_paid = True
        booking.status = 'terjadwal'
        booking.save()
        
        messages.success(request, "Pembayaran berhasil! Jadwal Anda telah dikonfirmasi.")
        return redirect('booking_list')
        
    return render(request, 'pasien/booking_pay.html', {'booking': booking})