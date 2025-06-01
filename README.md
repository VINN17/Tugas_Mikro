# 🚧 BUILDING AUTOMATION SYSTEMS PADA POMPA DI JALAN TOL

## 📌 Deskripsi Proyek

**Building Automation Systems** ini dirancang untuk mengotomatisasi pengoperasian **pompa air di jalan tol**, guna mengatasi genangan atau banjir secara cepat dan efisien.  
Menggunakan sensor debit dan volume air, sistem ini secara otomatis menghidupkan atau mematikan pompa berdasarkan data real-time, sehingga dapat meningkatkan keamanan dan kenyamanan pengguna jalan.

> Proyek ini dikembangkan berbasis mikrokontroler **Arduino Mega 2560** dan dikombinasikan dengan sistem monitoring berbasis GUI, menawarkan solusi otomasi yang **andal**, **terjangkau**, dan **mudah diimplementasikan**.

---

## 🎯 Tujuan Proyek

- **Meningkatkan Efisiensi dan Produktivitas**  
  Sistem otomatisasi meminimalkan keterlibatan manusia, mengoptimalkan respons terhadap perubahan kondisi air.

- **Mengurangi Risiko Kesalahan Manual**  
  Otomasi berbasis sensor menghilangkan potensi kesalahan yang biasa terjadi dalam operasi manual.

- **Menyediakan Solusi Otomasi yang Terjangkau**  
  Dengan komponen yang mudah diakses dan biaya implementasi rendah, proyek ini menjadi pilihan ideal untuk banyak lokasi.

---

## 🛠️ Teknologi dan Komponen

| Komponen             | Spesifikasi                                  |
|----------------------|----------------------------------------------|
| Mikrokontroler        | Arduino Mega 2560                           |
| Sensor Debit Air      | Flow Sensor                                 |
| Sensor Volume Air     | Ultrasonic Sensor / Water Level Sensor      |
| Aktuator              | Pompa Air + Relay Module                    |
| Antarmuka Pengguna    | GUI berbasis Figma (Start/Stop, Monitoring)  |
| Komunikasi Data       | Kabel Serial (opsi Wireless untuk pengembangan lanjut) |

![Image](https://github.com/user-attachments/assets/4d12a8da-b201-4a60-b431-e0f226d4ba51)
---

## ⚙️ Cara Kerja Sistem

1. Sensor membaca **debit** dan **volume air** secara berkala.
2. Data dibandingkan dengan nilai **set point** yang telah ditentukan.
3. **Logika Kontrol**:
   - Jika **debit > set point** dan **volume > set point** → **Pompa ON**
   - Jika **debit ≤ set point** dan **volume ≤ set point** → **Pompa OFF**
4. Status pompa dan data sensor dikirim ke GUI untuk **monitoring real-time**.
5. Operator dapat melakukan **manual override** melalui GUI bila diperlukan.

---

## 🧩 Diagram Alur Sistem

<img src="./path/to/your/diagram.png" alt="Diagram Alur Sistem" 10="50" height="10">



**Penjelasan Alur:**
1. Sistem dimulai (Start).
2. Masuk ke tampilan **GUI**.
3. Pengguna memilih mode:
   - **Mode Auto**:
     - Membaca data sensor debit dan volume air.
     - Data sensor dikirim dari **AVR** ke **pyserial**.
     - Data dibandingkan dengan nilai **SetPoint**.
       - Jika **lebih besar** dari SetPoint → **Pompa ON**.
       - Jika **kurang dari/sama dengan** SetPoint → **Pompa OFF**.
   - **Mode Manual**:
     - Pengguna dapat memilih **START** untuk menghidupkan pompa.
     - Atau memilih **STOP** untuk mematikan pompa.
4. Setelah pompa menyala, air dipompa menuju **saluran pembuangan utama**.
5. Proses berulang hingga sistem dimatikan (END).

![Image](https://github.com/user-attachments/assets/c417c9df-479f-43a0-807a-b9347ed5da0f)
---

## 🌟 Kelebihan Proyek Ini

- **Real-Time Response** terhadap kondisi genangan.
- **Monitoring Terpusat** memudahkan kontrol banyak pompa dari satu lokasi.
- **Fleksibilitas** untuk integrasi ke sistem SCADA atau IoT di masa depan.
- **Biaya Implementasi Efisien**, cocok untuk deployment skala besar.
- **Scalable Design**, mendukung pengembangan tambahan seperti alarm, SMS alert, atau integrasi cloud.

---

## 📈 Potensi Pengembangan ke Depan

- Integrasi dengan **IoT Cloud Platform** untuk akses global.
- Notifikasi berbasis **SMS/WhatsApp** saat status kritis.
- Prediksi genangan berbasis **Machine Learning** dari data debit air historis.
- Integrasi ke dalam **Smart City Infrastructure**.

---

## 🤝 Dukungan dan Kolaborasi

Kami membuka peluang kolaborasi dengan pihak ketiga seperti:

- Investor yang tertarik pada bidang **infrastruktur cerdas**.
- Pemerintah atau operator jalan tol yang membutuhkan sistem pengendalian banjir otomatis.
- Perusahaan teknologi yang ingin mengembangkan solusi otomasi skala besar.

> 🚀 Mari bersama-sama membangun infrastruktur jalan tol yang lebih aman, cerdas, dan efisien.

---

# 📋 Struktur Tim

| NRP        | Nama     | Jobdesk             |
|------------|----------|---------------------|
| 2123600010 | Imam     | Project Manager     |
| 2123600014 | Ferri    | PCB Designer         |
| 2123600004 | Robith   | Hardware Specialist  |
| 2123600030 | Zach     | Software Developer   |
| 2123600023 | Choirul  | 3D Designer          |
| 2123600019 | Andira   | Non-Technical        |

---

# 📩 Hubungi Kami

Untuk pertanyaan, kolaborasi, atau demonstrasi proyek, silakan hubungi kami melalui email:

**✉️ buildingautomation.tol@gmail.com**
