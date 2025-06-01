# 🚧 BUILDING AUTOMATION SYSTEMS UNTUK POMPA AIR DI JALAN TOL

\<div align="center">

&#x20; \<img src="[https://github.com/user-attachments/assets/cc067f5f-29a9-47e8-8fe2-f559c3799954](https://github.com/user-attachments/assets/cc067f5f-29a9-47e8-8fe2-f559c3799954)">

\</div>\\

## 📌 Deskripsi Proyek

**Building Automation Systems** ini dirancang untuk mengotomatisasi pengoperasian **pompa air pada jalan tol** guna mengatasi genangan atau banjir secara cepat dan efisien.

Dengan memanfaatkan sensor debit dan volume air, sistem ini mampu menghidupkan atau mematikan pompa secara otomatis berdasarkan data real-time, sehingga meningkatkan **keamanan** dan **kenyamanan** pengguna jalan.

> Dikembangkan berbasis **Arduino Mega 2560** dan sistem monitoring berbasis GUI, proyek ini menawarkan solusi otomasi yang **andal**, **efisien**, dan **mudah diimplementasikan**.

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

!\[Image]\([https://github.com/user-attachments/assets/1327b8de-43a2-474f-bb94-4d029d60099e](https://github.com/user-attachments/assets/1327b8de-43a2-474f-bb94-4d029d60099e))

| Komponen           | Spesifikasi                                  |
| ------------------ | -------------------------------------------- |
| Mikrokontroler     | Arduino Mega 2560                            |
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

!\[Image]\([https://github.com/user-attachments/assets/c8edc639-7d1b-4b6b-8df4-81f207d4f9f1](https://github.com/user-attachments/assets/c8edc639-7d1b-4b6b-8df4-81f207d4f9f1))

**Penjelasan Alur:**

* Sistem dimulai melalui tampilan GUI.

* Pengguna memilih mode: **Auto** atau **Manual**.

  * **Auto**: sensor membaca data → kirim ke GUI → kontrol pompa otomatis.
  * **Manual**: pengguna dapat menyalakan/mematikan pompa secara langsung.

* Sistem akan terus berjalan sampai dihentikan manual oleh operator.

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

!\[Image]\([https://github.com/user-attachments/assets/1b4c1482-4e50-4561-bc47-0bbc0ea77da7](https://github.com/user-attachments/assets/1b4c1482-4e50-4561-bc47-0bbc0ea77da7))

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

> 🚀 Mari bersama kita ciptakan masa depan infrastruktur jalan tol yang lebih **cerdas**, **aman**, dan **berkelanjutan**.
