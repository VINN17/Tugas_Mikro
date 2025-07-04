import tkinter as tk
from tkinter import PhotoImage, messagebox, ttk # Import ttk untuk styling
import os
import serial
import threading
import queue
import time
from collections import deque
from pathlib import Path

# Untuk grafik real-time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# === CONFIG ===
SERIAL_PORT = 'COM23'  # <--- PASTIKAN INI SESUAI DENGAN PORT SERIAL MIKROKONTROLER ANDA
BAUD_RATE = 115200
THRESHOLD_ADC0 = 800   # Threshold untuk water level (raw ADC value)
THRESHOLD_ADC1 = 600   # Threshold untuk pressure (raw ADC value)

# Range konversi ADC ke nilai fisik
ADC_MAX_VALUE = 1023 # Untuk ADC 10-bit

# Water Level: 0-5 meter
WATER_LEVEL_MAX_METER = 5.0
WATER_LEVEL_ON_THRESHOLD_METER = 2.5 # Pompa nyala jika > 3 meter
WATER_LEVEL_OFF_THRESHOLD_METER = 0.5 # Pompa mati jika <= 0.5 meter

# Pressure: 0-10 Bar (asumsi standar untuk sensor pompa air)
PRESSURE_MAX_BAR = 10.0 
PRESSURE_MOTOR_OFF_THRESHOLD_BAR = 1.0 # Motor mati jika pressure <= 1.0 Bar

# Path untuk aset gambar
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\ia088\Downloads\projek hendri\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# --- Queue untuk Komunikasi Antar Thread ---
# Data yang diterima dari serial akan dimasukkan ke queue ini oleh thread serial reader
# dan dibaca oleh main GUI thread.
serial_data_queue = queue.Queue()

# --- Fungsi Thread Pembaca Serial ---
def serial_reader_thread(ser_instance, data_queue):
    """
    Fungsi ini berjalan di thread terpisah untuk membaca data dari port serial.
    Data yang diterima akan dimasukkan ke dalam queue.
    """
    print(f"Serial reader thread started for {ser_instance.port}")
    while True:
        try:
            if ser_instance.is_open and ser_instance.in_waiting > 0:
                # Baca satu baris penuh yang diakhiri dengan newline/carriage return
                line = ser_instance.readline().decode('utf-8').strip()
                if line:
                    data_queue.put(line) # Masukkan data ke queue
                    # print(f"Received (thread): {line}") # Debugging
            time.sleep(0.01) # Beri sedikit delay agar tidak terlalu membebani CPU
        except serial.SerialException as e:
            print(f"Serial port error in thread: {e}")
            break # Keluar dari loop jika ada error serial
        except Exception as e:
            print(f"An unexpected error occurred in serial thread: {e}")
            break # Keluar dari loop jika ada error lain

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("BAS Pump Monitoring System")
        self.master.geometry("1280x800")
        self.master.resizable(False, False)
        self.master.configure(bg="#FFFFFF")

        # Variabel status
        self.adc_values = {'ADC0': 0, 'ADC1': 0}
        self.monitoring = False
        self.out_states = {1: False, 2: False, 3: False} # OUT1: Pompa, OUT3: Lampu Motor
        self.mode = 0 # 0 for Manual, 1 for Auto
        self.state = 0 # 0 for OFF, 1 for ON (for pump)
        self.log = 0 # Bitmask for logging/grafik (0: None, 1: Log, 2: Grafik, 3: Keduanya)

        # Inisialisasi Serial Port
        self.ser = None
        
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            time.sleep(2) # Tunggu sebentar agar Arduino siap
            print(f"Koneksi serial ke {self.ser.port} berhasil dibuka.")
            
            # Mulai thread pembaca serial
            self.serial_thread = threading.Thread(target=serial_reader_thread, args=(self.ser, serial_data_queue), daemon=True)
            self.serial_thread.start()

            # Kirim perintah awal ke mikrokontroler
            self.send_command_to_mcu("DO_Set") # Aktifkan Digital Output
            self.send_command_to_mcu("ADC_Set") # Aktifkan ADC secara global
            self.send_command_to_mcu("ADC_Loop") # Mulai ADC Loop untuk semua channel
            print("Initial commands (DO_Set, ADC_Set, ADC_Loop) sent.")

            self.send_command_to_mcu(f"OUT1{1}")
            
        except serial.SerialException as e:
            messagebox.showerror("Serial Port Error", f"Tidak dapat membuka port serial {SERIAL_PORT}:\n{e}\nPastikan mikrokontroler terhubung dan port yang benar dipilih.")
            print(f"Error: Tidak dapat membuka port serial {SERIAL_PORT} - {e}")
            self.master.destroy() # Tutup jendela jika gagal membuka serial port
            return

        # === GUI Elements ===
        self.canvas = tk.Canvas(
            self.master,
            bg="#FFFFFF",
            height=800,
            width=1280,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        # Muat semua gambar
        self.load_images()
        self.place_images()
        
        # --- Konfigurasi Style untuk Progress Bar ---
        self.style = ttk.Style()
        
        # Gaya baru untuk Progress Bar (Baby Blue)
        # Warna biru muda yang mendekati gambar
        baby_blue_fill = "#87CEEB" # Sky Blue
        baby_blue_trough = "#E0F2F7" # Light Cyan (untuk area tidak terisi)
        # Untuk border/efek 3D, kita bisa gunakan warna yang sedikit lebih gelap atau terang
        baby_blue_border = "#6495ED" # Cornflower Blue (untuk border/efek 3D)

        # Konfigurasi elemen 'bar' dan 'trough' dari progressbar
        # `troughcolor`: Warna background (area tidak terisi)
        # `background`: Warna bar terisi
        # `bordercolor`, `lightcolor`, `darkcolor`: Untuk efek 3D border
        # `relief`: Tipe relief (flat, sunken, raised, groove, ridge)
        # `borderradius`: Untuk sudut membulat (tidak didukung secara langsung oleh semua tema ttk)
        
        # Kita akan membuat style baru yang spesifik untuk progress bar kita
        self.style.element_create("progressbar.trough", "from", "clam")
        self.style.element_create("progressbar.pbar", "from", "clam")

        self.style.layout("BabyBlue.Horizontal.TProgressbar",
                          [('progressbar.trough', {'children':
                                                    [('progressbar.pbar', {'side': 'left', 'sticky': 'ns'})],
                                                    'sticky': 'nswe'})])
        
        self.style.configure("BabyBlue.Horizontal.TProgressbar",
                             troughcolor=baby_blue_trough,
                             background=baby_blue_fill,
                             bordercolor=baby_blue_border,
                             lightcolor=baby_blue_fill, # Coba warna yang sama untuk efek lebih halus
                             darkcolor=baby_blue_fill,  # Coba warna yang sama untuk efek lebih halus
                             relief="flat", # Coba flat untuk tampilan lebih modern
                             # borderradius=5 # borderradius tidak selalu didukung oleh semua tema/OS
                             )
        # Untuk efek "smooth" saat bergerak, itu adalah perilaku default dari progressbar Tkinter.
        # Untuk efek visual "smooth" pada bentuk (seperti rounded corners), ttk.Progressbar tidak mendukungnya secara langsung
        # melalui style untuk semua tema. Jika Anda ingin rounded corners yang sempurna, Anda mungkin perlu
        # menggambar progress bar secara manual di canvas atau menggunakan library lain.
        # Namun, dengan konfigurasi di atas, kita mendekati warna dan tampilan yang lebih bersih.


        self.create_text_elements()
        self.create_buttons()

        # Inisialisasi status pompa awal
        self.status_pompa(False) # Pompa awalnya OFF

        # Mulai pembaruan GUI dari Queue
        self.master.after(100, self.check_serial_queue) # Cek setiap 100ms

        # Set protokol penutupan jendela
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Inisialisasi gambar image_2 dan logic_log
        self.image_2_id = None # ID untuk image_2 di canvas
        self.file1 = None # PhotoImage object for image_2
        
        # --- Inisialisasi Log Aktivitas ---
        self.log_text = tk.Text(self.canvas, width=40, height=15, state='disabled', wrap='word', font=("Consolas", 10))
        # Posisi awal (akan diatur ulang oleh logic_log)
        self.log_text_id = self.canvas.create_window(
            639.0, 299.0, # Posisi default, akan diubah
            window=self.log_text,
            anchor="center",
            width=300, # Lebar log
            height=250, # Tinggi log
            state='hidden' # Sembunyikan secara default
        )
        self.add_log_entry("Sistem dimulai.")

        # --- Inisialisasi Grafik Real-time ---
        self.data_adc0_graph = deque(maxlen=100)
        self.data_adc1_graph = deque(maxlen=100)
        self.time_data_graph = deque(maxlen=100)

        self.fig, self.ax1 = plt.subplots(figsize=(4, 2.5), dpi=100)
        self.ax2 = self.ax1.twinx() # Sumbu Y kedua untuk ADC1
        
        self.line1, = self.ax1.plot([], [], 'g-', label='Water Level (m)') # Hijau untuk Water Level
        self.line2, = self.ax2.plot([], [], 'o-', color='orange', label='Pressure (Bar)') # Oranye untuk Pressure

        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Water Level (m)", color='g')
        self.ax2.set_ylabel("Pressure (Bar)", color='orange')
        
        self.ax1.tick_params(axis='y', labelcolor='g')
        self.ax2.tick_params(axis='y', labelcolor='orange')
        
        # Batas Y untuk Water Level (0-5 meter)
        self.ax1.set_ylim(0, WATER_LEVEL_MAX_METER * 1.1) 
        # Batas Y untuk Pressure (0-10 Bar)
        self.ax2.set_ylim(0, PRESSURE_MAX_BAR * 1.1) 

        self.fig.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95))
        self.fig.tight_layout() # Menyesuaikan layout agar label tidak tumpang tindih

        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.graph_widget = self.graph_canvas.get_tk_widget()
        # Posisi awal (akan diatur ulang oleh logic_log)
        self.graph_widget_id = self.canvas.create_window(
            639.0, 299.0, # Posisi default, akan diubah
            window=self.graph_widget,
            anchor="center",
            width=400, # Lebar grafik
            height=250, # Tinggi grafik
            state='hidden' # Sembunyikan secara default
        )
        self.ani = animation.FuncAnimation(self.fig, self.animate_graph, interval=200, blit=False) # Update setiap 200ms

        self.logic_log(0) # Panggil sekali untuk inisialisasi awal (menampilkan image_2 default)

    def load_images(self):
        """Memuat semua PhotoImage objek."""
        self.image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        self.image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
        self.image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
        self.image_image_5 = PhotoImage(file=relative_to_assets("image_5.png"))
        self.image_image_6 = PhotoImage(file=relative_to_assets("image_6.png"))
        self.image_image_7 = PhotoImage(file=relative_to_assets("image_7.png"))
        self.image_image_8 = PhotoImage(file=relative_to_assets("image_8.png"))
        self.image_image_9 = PhotoImage(file=relative_to_assets("image_9.png"))
        self.image_image_10 = PhotoImage(file=relative_to_assets("image_10.png"))
        self.image_image_11 = PhotoImage(file=relative_to_assets("image_11.png"))
        self.image_image_12 = PhotoImage(file=relative_to_assets("image_12.png"))
        
        # Gambar untuk status pompa
        self.image_image_13_1 = PhotoImage(file=relative_to_assets("image_13_1.png")) # OFF
        self.image_image_13_2 = PhotoImage(file=relative_to_assets("image_13_2.png")) # ON
        
        self.image_image_14 = PhotoImage(file=relative_to_assets("image_14.png"))
        self.image_image_15 = PhotoImage(file=relative_to_assets("image_15.png"))
        
        # Gambar untuk background nilai ADC (image_16 dan image_17)
        try:
            self.image_image_16 = PhotoImage(file=relative_to_assets("image_16.png"))
        except tk.TclError:
            print("Warning: image_16.png not found. Using placeholder.")
            self.image_image_16 = PhotoImage(width=100, height=50)
            self.image_image_16.put("red", to=(0,0,99,49))

        try:
            self.image_image_17 = PhotoImage(file=relative_to_assets("image_17.png"))
        except tk.TclError:
            print("Warning: image_17.png not found. Using placeholder.")
            self.image_image_17 = PhotoImage(width=100, height=10)
            self.image_image_17.put("blue", to=(0,0,99,49))
        
        # Gambar tombol
        self.button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        self.button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
        self.img_start_default = PhotoImage(file=relative_to_assets("button_2.png"))
        self.img_stop_default = PhotoImage(file=relative_to_assets("button_4.png"))
        self.img_start_pressed = PhotoImage(file=relative_to_assets("button_2_1.png"))
        self.img_stop_pressed = PhotoImage(file=relative_to_assets("button_4_1.png"))
        self.button_image_5 = PhotoImage(file=relative_to_assets("button_5.png"))
        self.button_image_6 = PhotoImage(file=relative_to_assets("button_6.png"))

        # Gambar untuk logic_log (image_2)
        self.image_2_default = PhotoImage(file=relative_to_assets("image_2.png"))
        self.image_2_log1 = PhotoImage(file=relative_to_assets("image_2_1.png"))
        self.image_2_log2 = PhotoImage(file=relative_to_assets("image_2_2.png"))
        self.image_2_log3 = PhotoImage(file=relative_to_assets("image_2_3.png"))

    def place_images(self):
        """Menempatkan semua gambar di canvas."""
        self.canvas.create_image(640.0, 400.0, image=self.image_image_1)
        # Simpan ID item canvas untuk image_3
        self.image_3_id = self.canvas.create_image(791.0, 449.0, image=self.image_image_3)
        self.canvas.create_image(559.0, 609.0, image=self.image_image_4)
        self.canvas.create_image(559.0, 552.0, image=self.image_image_5)
        self.canvas.create_image(435.0, 671.0, image=self.image_image_6)
        self.canvas.create_image(559.0, 475.0, image=self.image_image_7)
        self.canvas.create_image(559.0, 439.0, image=self.image_image_8)
        self.canvas.create_image(559.0, 265.0, image=self.image_image_9)
        self.canvas.create_image(558.5, 101.0, image=self.image_image_10)
        self.canvas.create_image(559.0, 125.0, image=self.image_image_11)
        self.canvas.create_image(559.0, 417.0, image=self.image_image_12)
        
        self.image_13_id = self.canvas.create_image(411.0, 210.0, image=self.image_image_13_1)
        self.canvas.create_image(619.0, 670.0, image=self.image_image_14)
        self.canvas.create_image(558.0, 328.0, image=self.image_image_15)

        # Background untuk nilai ADC
        self.canvas.create_image(633.0, 299.0, image=self.image_image_16)
        self.canvas.create_image(633.0, 355.0, image=self.image_image_17)

    def create_text_elements(self):
        """Membuat semua elemen teks dan progress bar di canvas."""
        self.canvas.create_text(470.0, 198.0, anchor="nw", text="Status Pompa", fill="#5276AB", font=("Inter", 20 * -1))
        self.canvas.create_text(400.0, 288.0, anchor="nw", text="Water Level:", fill="#5276AB", font=("Inter", 20 * -1))
        self.canvas.create_text(400.0, 344.0, anchor="nw", text="Pressure", fill="#5276AB", font=("Inter", 20 * -1))
        self.canvas.create_text(459.0, 112.0, anchor="nw", text="STATUS SYSTEM", fill="#5276AB", font=("Inter", 24 * -1))
        self.canvas.create_text(309.0, 20.0, anchor="nw", text="BUILDING AUTOMATION SYSTEM", fill="#5C5C5C", font=("Inter", 40 * -1))

        # --- Water Level (ADC0) Progress Bar and Value ---
        # Buat frame untuk menampung progress bar dan label
        self.frame_adc0 = tk.Frame(self.canvas, bg="#FFFFFF") 
        self.adc0_progressbar = ttk.Progressbar(self.frame_adc0, orient="horizontal", length=120, mode="determinate", style="BabyBlue.Horizontal.TProgressbar") # Menggunakan gaya baru
        self.adc0_progressbar.pack(side=tk.LEFT, padx=(0, 10)) # Progress bar di kiri frame

        self.adc0_value_label = tk.Label(self.frame_adc0, text="---", font=("Arial", 14, "bold"), bg="#FFFFFF", fg="#0000FF")
        self.adc0_value_label.pack(side=tk.LEFT) # Label nilai di kanan progress bar

        # Tempatkan frame di canvas menggunakan create_window
        # Koordinat 633.0, 300.0 adalah pusat dari image_16, kita akan menempatkan frame di sana
        self.canvas.create_window(
            633.0, # Center X
            300.0, # Center Y
            window=self.frame_adc0,
            anchor="center" # Pusatkan frame di koordinat yang ditentukan
        )

        # --- Pressure (ADC1) Progress Bar and Value ---
        self.frame_adc1 = tk.Frame(self.canvas, bg="#FFFFFF")
        self.adc1_progressbar = ttk.Progressbar(self.frame_adc1, orient="horizontal", length=120, mode="determinate", style="BabyBlue.Horizontal.TProgressbar") # Menggunakan gaya baru
        self.adc1_progressbar.pack(side=tk.LEFT, padx=(0, 10))

        self.adc1_value_label = tk.Label(self.frame_adc1, text="---", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#0000FF")
        self.adc1_value_label.pack(side=tk.LEFT)

        # Tempatkan frame di canvas menggunakan create_window
        # Koordinat 633.0, 355.0 adalah pusat dari image_17
        self.canvas.create_window(
            633.0, # Center X
            355.0, # Center Y
            window=self.frame_adc1,
            anchor="center"
        )

    def create_buttons(self):
        """Membuat semua tombol di GUI."""
        self.btn_auto = tk.Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.tombol_mode_auto,
            relief="flat"
        )
        self.btn_auto.place(x=406.0, y=651.0, width=62.0, height=41.0)

        self.btn_manual = tk.Button(
            image=self.button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.tombol_mode_manual,
            relief="flat"
        )
        self.btn_manual.place(x=521.0, y=651.0, width=60.0, height=40.0)

        self.btn_start = tk.Button(
            image=self.img_start_default,
            borderwidth=0,
            highlightthickness=0,
            command=self.tombol_state_off,
            relief="flat"
        )
        self.btn_start.place(x=602.0, y=646.0, width=50.0, height=51.0)

        self.btn_stop = tk.Button(
            image=self.img_stop_default,
            borderwidth=0,
            highlightthickness=0, 
            command=self.tombol_state_on,
            relief="flat"
        )
        self.btn_stop.place(x=670.0, y=646.0, width=50.0, height=51.0)
        
        self.btn_log = tk.Button(
            image=self.button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=self.tombol_data_log,
            relief="flat"
        )
        self.btn_log.place(x=804.0, y=191.0, width=37.0, height=190.0)

        self.btn_grafik = tk.Button(
            image=self.button_image_6,
            borderwidth=0,
            highlightthickness=0,
            command=self.tombol_data_grafik,
            relief="flat"
        )
        self.btn_grafik.place(x=804.0, y=433.0, width=37.0, height=283.0)

    def send_command_to_mcu(self, command):
        """Mengirim perintah ke mikrokontroler."""
        if self.ser and self.ser.is_open:
            self.ser.write(f"{command}\r\n".encode('utf-8'))
            print(f"Sent: {command}")
        else:
            print("Serial port not open. Cannot send command.")

    def add_log_entry(self, message):
        """Menambahkan entri ke log aktivitas."""
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END) # Auto-scroll ke bawah
        self.log_text.configure(state='disabled')

    def animate_graph(self, i):
        """Fungsi untuk memperbarui grafik secara real-time."""
        # Ambil data terbaru dari adc_values
        current_time = time.time()
        
        # Konversi nilai ADC ke satuan fisik
        water_level_m = (self.adc_values['ADC0'] / ADC_MAX_VALUE) * WATER_LEVEL_MAX_METER
        pressure_bar = (self.adc_values['ADC1'] / ADC_MAX_VALUE) * PRESSURE_MAX_BAR

        self.data_adc0_graph.append(water_level_m)
        self.data_adc1_graph.append(pressure_bar)
        self.time_data_graph.append(current_time)

        # Hapus data lama jika melebihi batas maxlen
        if len(self.time_data_graph) > 1:
            # Atur sumbu X agar menunjukkan waktu relatif atau rentang waktu yang relevan
            # Misalnya, tampilkan 10 detik terakhir
            min_time = self.time_data_graph[0]
            max_time = self.time_data_graph[-1]
            self.ax1.set_xlim(min_time, max_time)
            
            # Perbarui data plot
            self.line1.set_data(list(self.time_data_graph), list(self.data_adc0_graph))
            self.line2.set_data(list(self.time_data_graph), list(self.data_adc1_graph))

            # Auto-skala sumbu Y jika diperlukan (opsional, sudah diatur ylim di init)
            # self.ax1.relim()
            # self.ax1.autoscale_view(scalex=False) # Hanya skala Y
            # self.ax2.relim()
            # self.ax2.autoscale_view(scalex=False) # Hanya skala Y

        return self.line1, self.line2, # Return objek yang diubah untuk blitting (jika blit=True)


    def check_serial_queue(self):
        """
        Memeriksa queue data serial dan memperbarui GUI.
        Fungsi ini dipanggil secara berkala oleh window.after().
        """
        while not serial_data_queue.empty():
            line = serial_data_queue.get()
            # print(f"Processing from queue: {line}") # Debugging

            # Parsing data yang diterima (misal: "ADC0=512", "IN0=1")
            if line.startswith("ADC"):
                try:
                    parts = line.split('=')
                    if len(parts) == 2:
                        channel_str = parts[0].replace("ADC", "")
                        value_str = parts[1]
                        channel = int(channel_str)
                        value = int(value_str)
                        
                        # Asumsi ADC 10-bit, nilai max 1023
                        percentage = (value / ADC_MAX_VALUE) * 100 

                        if channel == 0:
                            self.adc_values['ADC0'] = value
                            self.adc0_progressbar['value'] = percentage
                            # Konversi ke meter untuk tampilan
                            water_level_m = (value / ADC_MAX_VALUE) * WATER_LEVEL_MAX_METER
                            self.adc0_value_label.config(text=f"{water_level_m:.2f} m")
                            # Tambahkan ke log jika aktif
                            if (self.log & 1) != 0:
                                self.add_log_entry(f"Water Level: {water_level_m:.2f} m (ADC: {value})")

                        elif channel == 1:
                            self.adc_values['ADC1'] = value
                            self.adc1_progressbar['value'] = percentage
                            # Konversi ke Bar untuk tampilan
                            pressure_bar = (value / ADC_MAX_VALUE) * PRESSURE_MAX_BAR
                            self.adc1_value_label.config(text=f"{pressure_bar:.2f} Bar")
                            # Tambahkan ke log jika aktif
                            if (self.log & 1) != 0:
                                self.add_log_entry(f"Pressure: {pressure_bar:.2f} Bar (ADC: {value})")
                        
                except ValueError:
                    print(f"Error parsing ADC data: {line}")
            elif line.startswith("IN"):
                try:
                    parts = line.split('=')
                    if len(parts) == 2:
                        channel_str = parts[0].replace("IN", "")
                        state_str = parts[1]
                        channel = int(channel_str)
                        state = int(state_str)
                        # Contoh: print digital input state
                        print(f"Digital Input {channel}: {state}")
                        if (self.log & 1) != 0:
                            self.add_log_entry(f"Digital Input {channel}: {'HIGH' if state else 'LOW'}")
                except ValueError:
                    print(f"Error parsing Digital Input data: {line}")
        
        # Logika mode otomatis (jika diaktifkan)
        # Konversi nilai ADC ke satuan fisik untuk logika kontrol
        current_water_level_m = (self.adc_values['ADC0'] / ADC_MAX_VALUE) * WATER_LEVEL_MAX_METER
        current_pressure_bar = (self.adc_values['ADC1'] / ADC_MAX_VALUE) * PRESSURE_MAX_BAR

        if self.mode == 1: # Jika mode Auto
            # Logika untuk OUT1 (Pompa) berdasarkan Water Level
            if current_water_level_m > WATER_LEVEL_ON_THRESHOLD_METER and self.state == 0:
                # Air di bawah 0.5 meter dan pompa nyala -> Matikan pompa
                self.state = 1
                self.send_command_to_mcu(f"OUT1{0}")
                self.status_pompa(True)
                self.add_log_entry(f"Auto Mode: Water Level LOW ({current_water_level_m:.2f}m <= {WATER_LEVEL_OFF_THRESHOLD_METER}m), turning pump OFF.")

            elif current_water_level_m <= WATER_LEVEL_OFF_THRESHOLD_METER and self.state == 1:
                
                # Air di atas 3 meter dan pompa mati -> Nyalakan pompa
                self.state = 0
                self.send_command_to_mcu(f"OUT1{1}")
                self.status_pompa(False)
                self.add_log_entry(f"Auto Mode: Water Level HIGH ({current_water_level_m:.2f}m > {WATER_LEVEL_ON_THRESHOLD_METER}m), turning pump ON.")
            # Logika untuk mematikan pompa berdasarkan Pressure, hanya jika pompa sedang menyala
            if self.state == 1 and current_pressure_bar <= PRESSURE_MOTOR_OFF_THRESHOLD_BAR:
                # Pompa sedang nyala, tapi pressure rendah (0-1 bar) -> Matikan pompa untuk proteksi
                self.state = 0
                self.send_command_to_mcu(f"OUT3{int(self.state)}")
                self.status_pompa(False)
                self.add_log_entry(f"Auto Mode: WARNING! Pressure LOW ({current_pressure_bar:.2f} Bar <= {PRESSURE_MOTOR_OFF_THRESHOLD_BAR} Bar), turning pump OFF for protection.")
            
            # Logika untuk OUT3 (Lampu Motor) berdasarkan Pressure (ADC1)
            # Asumsi OUT3 adalah lampu motor, dan aktif jika pressure tinggi
            current_lamp_motor_state = self.out_states[1]
            new_lamp_motor_state = current_pressure_bar > THRESHOLD_ADC1 # Menggunakan threshold raw ADC untuk lampu
            if new_lamp_motor_state != current_lamp_motor_state:
                self.out_states[1] = new_lamp_motor_state
                self.send_command_to_mcu(f"OUT1{int(new_lamp_motor_state)}")
                self.add_log_entry(f"Auto Mode: Pressure ({current_pressure_bar:.2f} Bar), updating Lamp Motor to {new_lamp_motor_state}.")


        # Jadwalkan pemanggilan fungsi ini lagi setelah 100 ms
        self.master.after(100, self.check_serial_queue)

    # --- LOGIC FUNCTIONS (Dipindahkan ke dalam kelas) ---
    def tombol_data_log(self):
        """Mengatur bit untuk logging data."""
        prev_log_state = (self.log & 1) != 0
        if prev_log_state:
            self.log &= ~1 # Clear bit 0
            self.add_log_entry("Logging dinonaktifkan.")
        else:
            self.log |= 1 # Set bit 0
            self.add_log_entry("Logging diaktifkan.")
        self.logic_log(self.log)
        
    def tombol_data_grafik(self):
        """Mengatur bit untuk menampilkan grafik."""
        prev_graph_state = (self.log & 2) != 0
        if prev_graph_state:
            self.log &= ~2 # Clear bit 1
            self.add_log_entry("Grafik dinonaktifkan.")
        else:
            self.log |= 2 # Set bit 1
            self.add_log_entry("Grafik diaktifkan.")
        self.logic_log(self.log)
        
    def tombol_mode_auto(self):
        """Mengatur mode sistem ke Otomatis."""
        if self.mode != 1:
            self.mode = 1
            print(f"Mode: Auto (Nilai mode sekarang: {self.mode})")
            self.add_log_entry("Mode diubah ke Otomatis.")
            self.toggle_PB(False) # Nonaktifkan tombol manual saat mode auto
        
    def tombol_mode_manual(self):
        """Mengatur mode sistem ke Manual."""
        if self.mode != 0:
            self.mode = 0
            print(f"Mode: Manual (Nilai mode sekarang: {self.mode})")
            self.add_log_entry("Mode diubah ke Manual.")
            self.toggle_PB(True) # Aktifkan tombol manual saat mode manual
            # Jika pompa sedang ON karena auto, matikan dulu saat beralih ke manual
            if self.state == 0:
                self.state = 1
                self.send_command_to_mcu(f"OUT1{int(self.state)}")
                self.status_pompa(False)
                self.add_log_entry("Pompa dimatikan saat beralih ke Mode Manual.")


    def tombol_state_on(self):
        """Menghidupkan pompa secara manual."""
        if self.mode == 0: # Hanya jika mode Manual
            if self.state == 0:
                self.state = 1
                self.send_command_to_mcu(f"OUT1{int(self.state)}")
                self.status_pompa(False) # Update visual status pompa
                self.add_log_entry("Manual: Pompa dihidupkan.")
            print(f"Nilai state sekarang: {self.state}")
        else:
            print("Cannot control manually in Auto Mode.")
            messagebox.showinfo("Mode Error", "Tidak dapat mengontrol secara manual dalam Mode Otomatis.")

    def tombol_state_off(self):
        """Mematikan pompa secara manual."""
        if self.mode == 0: # Hanya jika mode Manual
            if self.state == 1:
                self.state = 0
                self.send_command_to_mcu(f"OUT1{int(self.state)}")
                self.status_pompa(True) # Update visual status pompa
                self.add_log_entry("Manual: Pompa dimatikan.")
            print(f"Nilai state sekarang: {self.state}")
        else:
            print("Cannot control manually in Auto Mode.")
            messagebox.showinfo("Mode Error", "Tidak dapat mengontrol secara manual dalam Mode Otomatis.")
            
    def status_pompa(self, is_started):
        """Memperbarui gambar status pompa di GUI."""
        if is_started:
            self.canvas.itemconfig(self.image_13_id, image=self.image_image_13_2)
        else:
            self.canvas.itemconfig(self.image_13_id, image=self.image_image_13_1)
            
    def toggle_PB(self, enable_manual_buttons):
        """Mengaktifkan/menonaktifkan tombol Start/Stop manual."""
        if enable_manual_buttons:
            self.btn_start.config(image=self.img_start_default, state=tk.NORMAL)
            self.btn_stop.config(image=self.img_stop_default, state=tk.NORMAL)
        else:
            self.btn_start.config(image=self.img_start_default, state=tk.DISABLED) # Gunakan default image
            self.btn_stop.config(image=self.img_stop_default, state=tk.DISABLED) # Gunakan default image

    def logic_log(self, x):
        """Memperbarui gambar image_2, log aktivitas, dan grafik berdasarkan nilai log."""
        
        # Sembunyikan semua elemen yang saling eksklusif terlebih dahulu
        if self.image_2_id is not None:
            self.canvas.itemconfig(self.image_2_id, state='hidden')
        self.canvas.itemconfig(self.log_text_id, state='hidden')
        self.canvas.itemconfig(self.graph_widget_id, state='hidden')

        # Koordinat dasar untuk area image_2 (pusat 639.0, 299.0)
        base_x = 639.0
        base_y = 299.0
        
        # Lebar elemen (sesuaikan jika perlu)
        # Log lebih kecil, grafik lebih besar
        log_width = 300
        graph_width = 400 
        element_height = 250 # Tinggi log dan grafik

        if (x & 1) != 0 and (x & 2) == 0: # Jika hanya bit 0 (Log) aktif (Log di atas image_2_1)
            print("Menampilkan Log Aktivitas di atas image_2_1.")
            self.file1 = self.image_2_log1
            
            # Posisi X untuk image_2_1 dan log (berdasarkan gambar, image_2_1 bergeser ke kiri)
            # Koordinat X untuk image_2_1 adalah 639.0 - 100 = 539.0
            img_x_offset = -100 # Offset dari base_x untuk image_2_1
            
            # Posisikan log_text di atas image_2_1
            self.canvas.coords(self.log_text_id, base_x + img_x_offset-355, base_y)
            self.canvas.itemconfig(self.log_text_id, state='normal', width=log_width, height=element_height)
            
            # Tampilkan image_2_1 sebagai latar belakang
            if self.image_2_id is None:
                self.image_2_id = self.canvas.create_image(base_x + img_x_offset, base_y, image=self.file1)
            else:
                self.canvas.itemconfig(self.image_2_id, image=self.file1)
                self.canvas.coords(self.image_2_id, base_x + img_x_offset-50, base_y)
            self.canvas.itemconfig(self.image_2_id, state='normal')
            self.canvas.tag_lower(self.image_2_id, self.image_3_id) # Kirim ke belakang gambar image_3

        elif (x & 2) != 0 and (x & 1) == 0: # Jika hanya bit 1 (Grafik) aktif (Grafik di atas image_2_2)
            print("Menampilkan Grafik di atas image_2_2.")
            self.file1 = self.image_2_log2
            
            # Posisi X untuk image_2_2 dan grafik (berdasarkan gambar, image_2_2 bergeser ke kanan)
            # Koordinat X untuk image_2_2 adalah 639.0 + 110 = 749.0
            img_x_offset = 110 # Offset dari base_x untuk image_2_2
            
            # Posisikan grafik di atas image_2_2
            self.canvas.coords(self.graph_widget_id, base_x + img_x_offset+313, base_y)
            self.canvas.itemconfig(self.graph_widget_id, state='normal', width=graph_width, height=element_height)
            self.ani.event_source.start()
            
            # Tampilkan image_2_2 sebagai latar belakang
            if self.image_2_id is None:
                self.image_2_id = self.canvas.create_image(base_x + img_x_offset, base_y, image=self.file1)
            else:
                self.canvas.itemconfig(self.image_2_id, image=self.file1)
                self.canvas.coords(self.image_2_id, base_x + img_x_offset+65, base_y)
            self.canvas.itemconfig(self.image_2_id, state='normal')
            self.canvas.tag_lower(self.image_2_id, self.image_3_id)

        elif (x & 1) != 0 and (x & 2) != 0: # Jika kedua bit aktif (Log dan Grafik di atas image_2_3)
            print("Menampilkan Log (kiri) dan Grafik (kanan) di atas image_2_3.")
            self.file1 = self.image_2_log3
            
            # Tampilkan image_2_3 sebagai latar belakang (pusat di base_x, base_y)
            if self.image_2_id is None:
                self.image_2_id = self.canvas.create_image(base_x, base_y, image=self.file1)
            else:
                self.canvas.itemconfig(self.image_2_id, image=self.file1)
                self.canvas.coords(self.image_2_id, base_x+11, base_y)
            self.canvas.itemconfig(self.image_2_id, state='normal')
            self.canvas.tag_lower(self.image_2_id, self.image_3_id)

            # Hitung posisi untuk log dan grafik agar berdampingan di atas image_2_3
            # Asumsi image_2_3 berpusat di base_x, base_y
            # Kita ingin log di kiri dan grafik di kanan
            # Total lebar area yang akan diisi oleh log dan grafik
            # log_width = 300, graph_width = 400
            # Padding antar elemen
            padding_between = 20
            total_elements_width = log_width + padding_between + graph_width 
            
            # Posisi X untuk pusat log (geser ke kiri dari tengah area gabungan)
            log_x = base_x - (total_elements_width / 2) + (log_width / 2)
            
            # Posisi X untuk pusat grafik (geser ke kanan dari tengah area gabungan)
            graph_x = log_x + (log_width / 2) + padding_between + (graph_width / 2) 
            
            self.canvas.coords(self.log_text_id, log_x-245, base_y)
            self.canvas.itemconfig(self.log_text_id, state='normal', width=log_width, height=element_height)

            self.canvas.coords(self.graph_widget_id, graph_x+263, base_y)
            self.canvas.itemconfig(self.graph_widget_id, state='normal', width=graph_width, height=element_height)
            self.ani.event_source.start()

        else: # Jika tidak ada bit yang aktif (log = 0)
            print("Menampilkan Gambar Default (image_2_default).")
            self.file1 = self.image_2_default
            if self.image_2_id is None:
                self.image_2_id = self.canvas.create_image(base_x, base_y, image=self.file1)
            else:
                self.canvas.itemconfig(self.image_2_id, image=self.file1)
                self.canvas.coords(self.image_2_id, base_x, base_y)
            self.canvas.itemconfig(self.image_2_id, state='normal')
            self.canvas.tag_lower(self.image_2_id, self.image_3_id)

        # Jika grafik tidak aktif, hentikan animasinya untuk menghemat sumber daya
        if (x & 2) == 0 and self.ani.event_source:
             self.ani.event_source.stop()


    def on_closing(self):
        """Fungsi ini dipanggil saat jendela GUI ditutup."""
        if self.ser and self.ser.is_open:
            print("Menutup port serial...")
            self.ser.close()
        # Hentikan animasi matplotlib saat menutup aplikasi
        if hasattr(self, 'ani') and self.ani.event_source:
            self.ani.event_source.stop()
        plt.close(self.fig) # Tutup figure matplotlib
        self.master.destroy()

# === Main Program ===
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
