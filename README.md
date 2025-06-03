# 🚧 Building Automation System (BAS) untuk Pompa Air Jalan Tol
### Solusi Banjir dan Kemacetan saat Hujan Berkepanjangan

<div align="center">
  <img src="https://github.com/user-attachments/assets/cc067f5f-29a9-47e8-8fe2-f559c3799954">
</div>
<div align="center">
  <video width="300" controls>
    <source src="(https://github.com/user-attachments/assets/4135e06a-734f-496c-8481-714472587500)" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>

https://github.com/user-attachments/assets/4135e06a-734f-496c-8481-714472587500

## 📚 Daftar Isi

1. [📌 Deskripsi Proyek](#-deskripsi-proyek)
2. [🎯 Tujuan Proyek](#-tujuan-proyek)
3. [🛠️ Teknologi dan Komponen](#️-teknologi-dan-komponen)
4. [⚙️ Cara Kerja Sistem](#️-cara-kerja-sistem)
5. [🧩 Diagram Alur Sistem](#-diagram-alur-sistem)
6. [🌟 Keunggulan Proyek](#-keunggulan-proyek)
7. [📈 Potensi Pengembangan](#-potensi-pengembangan)
8. [🤝 Kolaborasi & Dukungan](#-kolaborasi--dukungan)
9. [👥 Struktur Tim](#-struktur-tim)
10. [📩 Hubungi Kami](#-hubungi-kami)

---

## 📌 Deskripsi Proyek

**Building Automation Systems** ini dirancang untuk mengotomatisasi pengoperasian **pompa air pada jalan tol** guna mengatasi genangan atau banjir secara cepat dan efisien.

Dengan memanfaatkan sensor debit dan volume air, sistem ini mampu menghidupkan atau mematikan pompa secara otomatis berdasarkan data real-time, sehingga meningkatkan **keamanan** dan **kenyamanan** pengguna jalan.

> Dikembangkan berbasis **Arduino Uno** dan sistem monitoring berbasis GUI, proyek ini menawarkan solusi otomasi yang **andal**, **efisien**, dan **mudah diimplementasikan**.

---

## 🎯 Tujuan Proyek

* **Efisiensi Operasional Maksimal**
  Sistem mengeliminasi keterlambatan manual dan mengoptimalkan respons terhadap kondisi air.

* **Minimalkan Risiko Human Error**
  Pengambilan keputusan berbasis data sensor menghindari kesalahan dalam penanganan banjir.

* **Solusi Otomasi Biaya Terjangkau**
  Menggunakan komponen yang tersedia di pasaran dengan biaya rendah, ideal untuk skalabilitas.

---

## 🛠️ Teknologi dan Komponen

![Image](https://github.com/user-attachments/assets/1327b8de-43a2-474f-bb94-4d029d60099e)

| Komponen           | Spesifikasi                                  |
| ------------------ | -------------------------------------------- |
| Mikrokontroler     | Arduino Uno                                  |
| Sensor Debit Air   | Pressure Sensor                              |
| Sensor Volume Air  | Ultrasonic / Water Level Sensor              |
| Aktuator           | Pompa Air + Relay Module                     |
| Antarmuka Pengguna | GUI berbasis Figma (Start/Stop, Monitoring)  |
| Komunikasi Data    | Serial / Wireless (pengembangan selanjutnya) |

---

## ⚙️ Cara Kerja Sistem

1. Sensor membaca **debit** dan **volume air** secara berkala.
2. Data dikirim ke mikrokontroler dan dibandingkan dengan nilai **set point**.
3. **Logika Kendali Otomatis**:

   * Jika data melebihi ambang → **Pompa ON**
   * Jika data aman → **Pompa OFF**
4. Status sistem ditampilkan pada GUI untuk **monitoring real-time**.
5. Operator dapat melakukan **manual override** dari GUI bila dibutuhkan.

---

## 🧩 Diagram Alur Sistem

![Image](https://github.com/user-attachments/assets/c8edc639-7d1b-4b6b-8df4-81f207d4f9f1)

**Penjelasan Alur:**

* Sistem dimulai melalui tampilan GUI.

* Pengguna memilih mode: **Auto** atau **Manual**.

  * **Auto**: sensor membaca data → kirim ke GUI → kontrol pompa otomatis.
  * **Manual**: pengguna dapat menyalakan/mematikan pompa secara langsung.

* Sistem akan terus berjalan sampai dihentikan manual oleh operator.

---

## 💻 PCB

![Image](https://github.com/user-attachments/assets/2f61345b-46dd-41f9-9cba-4b920a82135a)

Diatas  merupakan desain PCB jadi 

---


## 🌟 Keunggulan Proyek

* ✅ **Respon Real-Time** terhadap potensi banjir.
* ✅ **Kontrol Terpusat & Mudah** dari satu GUI.
* ✅ **Terintegrasi dengan IoT/SCADA** untuk masa depan.
* ✅ **Desain Scalable** & mudah diadaptasi ke area baru.
* ✅ **Ramah Anggaran** untuk implementasi massal.

---

## 📈 Potensi Pengembangan

* 🌐 **Integrasi ke IoT Cloud**: akses global & notifikasi otomatis.
* 🔔 **Peringatan SMS/WhatsApp** saat kondisi kritis.
* 🧠 **Prediksi Banjir Berbasis AI**: analisis historis dengan Machine Learning.
* 🏙️ **Kompatibel dengan Smart City Infrastructure**.

---

## 🤝 Kolaborasi & Dukungan

Kami membuka peluang kerja sama dengan:

* 🔧 **Investor teknologi** yang tertarik pada otomasi infrastruktur.
* 🛣️ **Pemerintah / Operator Jalan Tol** untuk penerapan langsung.
* 🧪 **Startup atau perusahaan R\&D** yang ingin mengembangkan solusi pintar dan berdampak.

> 🎯 Kami siap melakukan presentasi, demo proyek, dan diskusi lanjutan bersama mitra strategis.

---

## 👥 Struktur Tim

![Image](https://github.com/user-attachments/assets/1b4c1482-4e50-4561-bc47-0bbc0ea77da7)

| NRP        | Nama    | Peran Utama              |
| ---------- | ------- | ------------------------ |
| 2123600010 | Imam    | Project Manager          |
| 2123600014 | Ferri   | Desain PCB               |
| 2123600004 | Robith  | Spesialis Hardware       |
| 2123600030 | Zach    | Pengembang Software      |
| 2123600023 | Choirul | Desainer 3D              |
| 2123600019 | Andira  | Non-Teknis & Dokumentasi |

---

## 📩 Hubungi Kami

📧 Untuk kerja sama, pertanyaan, atau demo proyek:

**Email Project Manager**: [immarfn17@gmail.com](mailto:immarfn17@gmail.com)

https://github.com/user-attachments/assets/88c9bd39-f75d-4216-a4de-ee6d6c01959d
> 🚀 Mari bersama kita ciptakan masa depan infrastruktur jalan tol yang lebih **cerdas**, **aman**, dan **berkelanjutan**.
