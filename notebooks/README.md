# 🧠 Model Training & Data Preparation

Folder ini berisi Jupyter Notebook yang digunakan untuk melakukan proses _training_ model YOLOv8x-OBB.

## 📄 Isi Folder
- **`YOLOv8_OBB_Training_Pipeline.ipynb`**: Notebook komprehensif yang berisi seluruh siklus hidup model AI, mulai dari:
  - Instalasi pustaka Ultralytics.
  - Pengunduhan dataset DOTAv1 dari server eksternal/Kaggle.
  - Konversi format DOTA ke format YOLO OBB (Oriented Bounding Box).
  - Eksekusi _training_ model YOLOv8x-OBB.
  - Proses validasi dan ekspor *weights* (file `.pt`).

## 🚀 Cara Menjalankan (Rekomendasi)
Notebook ini sangat disarankan untuk dijalankan pada environment berbasis Cloud yang memiliki akses GPU tinggi secara gratis, seperti:
- **Kaggle Notebooks** (Sangat disarankan karena dataset DOTA tersedia secara publik di Kaggle).
- **Google Colab** (Membutuhkan penyesuaian sedikit pada bagian *download* dataset).

### Langkah-langkah di Kaggle:
1. Buat Notebook baru di Kaggle.
2. Atur Accelerator ke **GPU T4 x2** atau **P100**.
3. *File -> Import Notebook* dan pilih file `YOLOv8_OBB_Training_Pipeline.ipynb` ini.
4. Pastikan opsi *Internet* menyala di Settings.
5. Jalankan semua *cells* secara berurutan.
6. Setelah selesai, file `best.pt` dapat diunduh dari folder `runs/train/weights/` dan ditempatkan ke dalam folder `SIG_Deteksi_Bangunan/weights/` pada sistem *deployment* Streamlit lokal Anda.
