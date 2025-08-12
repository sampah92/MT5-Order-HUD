import tkinter as tk
import MetaTrader5 as mt5
from playsound import playsound, PlaysoundException
import threading
import ctypes # Diperlukan untuk membuat jendela "click-through" di Windows
import os # Import pustaka 'os' untuk menangani jalur file
import sys # Pustaka sys untuk mendapatkan jalur yang benar setelah PyInstaller
import pystray # Pustaka untuk ikon baki sistem
from PIL import Image # Pustaka untuk membuat gambar ikon
import win32api # Pustaka Windows API
import win32gui # Pustaka Windows API
import win32con # Konstanta untuk Windows API

# --- Konfigurasi ---
# Ganti dengan path MT5 terminal Anda jika diperlukan.
if not mt5.initialize():
    print("Inisialisasi MT5 gagal. Pastikan terminal MT5 sudah berjalan.")
    exit()

SOUND_OPEN = "open_order.wav"
SOUND_CLOSE = "close_order.wav"

def resource_path(relative_path):
    """
    Dapatkan jalur absolut ke sumber daya, bekerja untuk dev dan PyInstaller.
    """
    try:
        # Jalur dasar saat dikemas menjadi file .exe
        base_path = sys._MEIPASS
    except Exception:
        # Jalur dasar saat berjalan dalam mode pengembangan
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Fungsi untuk mendapatkan total profit/loss dan informasi posisi
def get_total_pl():
    """
    Mengambil semua posisi terbuka dan menghitung total profit/loss, total lot,
    dan menentukan jenis posisi serta simbol.
    """
    positions = mt5.positions_get()
    if positions is None:
        # Mengembalikan nilai default untuk profit, lot, dan list posisi
        return 0.0, 0.0, "---", "---", []

    total_profit = sum(position.profit for position in positions)
    total_lots = sum(position.volume for position in positions)

    # Menentukan jenis posisi (BUY, SELL, atau MIXED)
    position_types = [position.type for position in positions]
    if all(p_type == mt5.POSITION_TYPE_BUY for p_type in position_types):
        display_type = "BUY"
    elif all(p_type == mt5.POSITION_TYPE_SELL for p_type in position_types):
        display_type = "SELL"
    else:
        display_type = "MIXED"

    # Menentukan simbol (EURUSD, dll., atau MULTIPLE)
    position_symbols = [position.symbol for position in positions]
    if len(set(position_symbols)) == 1:
        # Hapus "EU" dari "EURUSD"
        display_currency = position_symbols[0]
        if len(display_currency) > 4:
            display_currency = display_currency[:4]
    else:
        display_currency = "MULTIPLE"

    return total_profit, total_lots, display_type, display_currency, positions

# --- Aplikasi UI ---

class MT5OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MT5 Overlay")
        
        # Buat jendela tanpa bingkai
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Mengatur warna latar belakang yang akan dibuat transparan
        self.root.configure(bg='black')

        # Ganti Label dengan Canvas
        # Mengurangi tinggi Canvas karena hanya ada satu baris teks
        self.canvas = tk.Canvas(
            self.root, 
            width=200, 
            height=40,
            bg='black', 
            highlightthickness=0 
        )
        self.canvas.pack()

        # Buat teks untuk P/L, Lots, dan lainnya di Canvas dalam satu baris
        self.profit_text = self.canvas.create_text(
            100, 20, # Posisi tengah Canvas
            text="--- --- 0.00 $0.00",
            font=("Helvetica", 14, "bold"),
            fill='white',
            tags="profit_tag"
        )
        
        self.root.withdraw()
        self.last_position_count = -1
        
        # Menyiapkan jendela agar transparan di tingkat Windows API
        self.set_transparency()
        
        self.icon = None
        self.setup_tray_icon()
        
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        self.update_data()
    
    def set_transparency(self):
        """
        Menggunakan Windows API untuk membuat jendela transparan dan "click-through".
        """
        try:
            hwnd = self.root.winfo_id()
            
            # Mendapatkan style jendela saat ini
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            # Menambahkan gaya transparansi
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW)
            
            # Menetapkan transparansi ke jendela (255 = solid, 0 = transparan)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)
        
        except Exception as e:
            print(f"Gagal menerapkan transparansi Windows API. Ini normal jika bukan di Windows: {e}")

    def setup_tray_icon(self):
        """
        Menyiapkan ikon baki sistem dengan menu.
        """
        image = Image.new('RGB', (64, 64), 'black')
        
        self.icon = pystray.Icon(
            'MT5 Overlay', 
            image, 
            'MT5 Overlay', 
            menu=pystray.Menu(
                pystray.MenuItem('Tampilkan', self.show_window),
                pystray.MenuItem('Keluar', self.exit_app)
            )
        )
        
        threading.Thread(target=self.icon.run, daemon=True).start()

    def play_sound_in_thread(self, sound_file):
        """
        Memutar file suara dalam thread terpisah agar UI tidak terblokir.
        """
        absolute_path = resource_path(sound_file)
        try:
            threading.Thread(target=playsound, args=(absolute_path,), daemon=True).start()
        except PlaysoundException as e:
            print(f"ERROR: File suara tidak ditemukan atau tidak dapat diputar: {absolute_path}")
        except Exception as e:
            print(f"Gagal memutar suara: {e}")

    def update_data(self):
        """
        Fungsi ini dipanggil secara berkala untuk memperbarui data
        dan mengontrol visibilitas jendela, termasuk memutar suara.
        """
        try:
            total_pl, total_lots, display_type, display_currency, positions = get_total_pl()
            current_position_count = len(positions)

            if self.last_position_count != -1:
                if current_position_count > self.last_position_count:
                    self.play_sound_in_thread(SOUND_OPEN)
                elif current_position_count < self.last_position_count:
                    self.play_sound_in_thread(SOUND_CLOSE)
            
            self.last_position_count = current_position_count

            if positions:
                self.show_window()

                if total_pl >= 0:
                    pl_color = '#39ff14'
                    pl_prefix = "+"
                else:
                    pl_color = '#ff073a'
                    pl_prefix = ""
                
                # Format string sesuai permintaan
                #formatted_text = f"{display_type} {display_currency} {total_lots:.2f} {pl_prefix}{total_pl:.2f}"
                formatted_text = f"{total_lots:.2f} {pl_prefix}{total_pl:.2f}"
                self.canvas.itemconfig(self.profit_text, text=formatted_text, fill=pl_color)
                
                # Perbarui ukuran Canvas agar pas dengan teks baru
                bbox_pl = self.canvas.bbox(self.profit_text)
                if bbox_pl:
                    width = bbox_pl[2] - bbox_pl[0] + 10 # Tambah padding
                    height = bbox_pl[3] - bbox_pl[1] + 10 # Tambah padding
                    self.canvas.config(width=width, height=height)
                    
                    # Pusatkan teks di Canvas yang baru
                    self.canvas.coords(self.profit_text, width/2, height/2)

            else:
                self.hide_window()

        except Exception as e:
            self.hide_window()
            self.canvas.itemconfig(self.profit_text, text="Error", fill='red')
            print(f"Error: {e}")

        self.root.after(1000, self.update_data)
    
    def hide_window(self):
        """Menyembunyikan jendela utama."""
        self.root.withdraw()
    
    def show_window(self):
        """Menampilkan kembali jendela utama."""
        self.root.deiconify()
    
    def exit_app(self, icon, item):
        """Menghentikan aplikasi."""
        icon.stop()
        self.root.destroy()
        mt5.shutdown()

# --- Jalankan Aplikasi ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MT5OverlayApp(root)
    root.mainloop()

mt5.shutdown()
