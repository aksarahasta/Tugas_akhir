from django.db import models

class Supplier(models.Model):
    nama_supplier = models.CharField(max_length=100)
    kategori = models.CharField(max_length=50, choices=[('obat','Obat'),('perlengkapan','Perlengkapan')])
    kontak = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_supplier

class Inventori(models.Model):
    nama = models.CharField(max_length=100)
    kategori = models.CharField(max_length=50, choices=[('obat','Obat'),('perlengkapan','Perlengkapan')])
    stok = models.IntegerField(default=0)
    harga = models.IntegerField(default=0)

    def __str__(self):
        return self.nama

class Cabang(models.Model):
    nama_cabang = models.CharField(max_length=100)
    alamat = models.TextField()
    kontak = models.CharField(max_length=100)
    manager = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_cabang

class BarangMasuk(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    inventori = models.ForeignKey(Inventori, on_delete=models.CASCADE)
    jumlah = models.IntegerField()
    tanggal = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.inventori.nama} dari {self.supplier.nama_supplier}"
