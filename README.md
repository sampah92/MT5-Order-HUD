# MT5 HUD (Heads-Up Display)

**MT5 HUD** adalah sebuah aplikasi overlay desktop yang ringan dan transparan untuk MetaTrader 5. Aplikasi ini dirancang untuk memberikan informasi trading penting secara real-time langsung di layar Anda tanpa mengganggu alur kerja.

---

### Fitur Utama

* **Tampilan Overlay Transparan**: Menampilkan ringkasan data trading (P/L, lot, posisi, mata uang) dalam overlay yang bersih dan tidak mencolok.
* **Data Real-Time**: Aplikasi ini terhubung langsung dengan terminal MT5 untuk menampilkan data terkini secara otomatis.
* **Notifikasi Audio**: Dapatkan pemberitahuan suara saat posisi trading baru dibuka atau ditutup.
* **Akses Cepat**: Kelola aplikasi dengan mudah melalui ikon di system tray (baki sistem) untuk menampilkan, menyembunyikan, atau menutupnya.

---

### Cara Menggunakan

1.  Pastikan terminal MetaTrader 5 Anda sudah berjalan.
2.  Jalankan file executable (`.exe`) dari aplikasi. Overlay akan muncul secara otomatis saat ada posisi trading yang terbuka.
3.  Klik kanan pada ikon aplikasi di baki sistem untuk opsi tambahan.

---

### Instalasi

Untuk menjalankan aplikasi ini dari kode sumbernya, Anda perlu menginstal pustaka Python yang diperlukan.

1.  Clone repositori ini
2.  Instal dependensi menggunakan `pip`:
    ```bash
    pip install -r requirements.txt
    ```

### Kontribusi

Jika Anda ingin membantu, silakan ikuti langkah-langkah berikut:

1.  Fork repositori ini.
2.  Buat branch baru (`git checkout -b feature/fitur-baru`).
3.  Lakukan perubahan dan commit (`git commit -am 'feat: menambahkan fitur baru'`).
4.  Push ke branch Anda (`git push origin feature/fitur-baru`).
5.  Buat **Pull Request** baru.

### Lisensi

**Lisensi MIT**.
