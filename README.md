# 🩺 Liver Disease Prediction App
 
Aplikasi Machine Learning berbasis web untuk memprediksi risiko penyakit liver menggunakan algoritma **XGBoost**.
 
🔗 **Live Demo:** [liver-disease-predict.streamlit.app](https://liver-disease-predict.streamlit.app/)
 
 
## 📖 Deskripsi Proyek
 
Proyek ini merupakan sistem prediksi penyakit liver yang dibangun dengan pendekatan Machine Learning. Pengguna cukup memasukkan data klinis seperti hasil tes darah dan informasi pasien, lalu model akan memberikan prediksi apakah pasien berpotensi mengidap penyakit liver atau tidak.
 
Model dilatih menggunakan **XGBoost Classifier** dan di-deploy sebagai aplikasi web interaktif menggunakan **Streamlit**.
 
 
## ✨ Fitur Utama
 
- 🔍 Prediksi risiko penyakit liver berbasis data klinis
- 📊 Visualisasi hasil prediksi yang informatif
- ⚡ Antarmuka web yang ringan dan responsif
- 🤖 Model Machine Learning XGBoost yang terlatih
- 🧪 Notebook eksplorasi dan analisis data lengkap
 
## 📁 Struktur Folder
 
```
Liver_Disease_Prediction/
│
├── .streamlit/                           # Konfigurasi tema Streamlit
│
├── app/                                  # Source code aplikasi web
│   └── app.py
│
├── data/
│   └── raw/
|       └── liver_patient_dataset.csv      
│
├── models/
│   └── liver_pipeline.joblib              # Model XGBoost yang sudah dilatih
│
├── notebook/
│   └── Liver_Disease_Prediction.ipynb     # Jupyter Notebook eksplorasi & pelatihan model
│
├── src/                                   # Modul Python pendukung (preprocessing, utils, dll.)
│
├── .gitignore
├── README.md
└── requirements.txt                       # Daftar dependensi Python
```
 
 
## 🛠️ Requirements
 
| Library        | Kegunaan                              |
|----------------|---------------------------------------|
| `streamlit`    | Framework aplikasi web interaktif     |
| `xgboost`      | Algoritma Machine Learning utama      |
| `scikit-learn` | Preprocessing & evaluasi model        |
| `pandas`       | Manipulasi dan analisis data          |
| `numpy`        | Komputasi numerik                     |
| `joblib`       | Menyimpan dan memuat model            |

 
## 🚀 Cara Menjalankan Secara Lokal
 
### 1. Clone Repository
 
```bash
git clone https://github.com/arifmfikri/Liver_Disease_Prediction.git
cd Liver_Disease_Prediction
```
 
### 2. Buat Virtual Environment (opsional tapi disarankan)
 
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```
 
### 3. Install Dependensi
 
```bash
pip install -r requirements.txt
```
 
### 4. Jalankan Aplikasi
 
```bash
streamlit run app/app.py
```
 
Aplikasi akan berjalan di `http://localhost:8501`
 
 
## 📊 Dataset
 
Dataset yang digunakan berisi informasi klinis pasien, seperti:
 
- Usia dan jenis kelamin
- Kadar bilirubin (total & langsung)
- Kadar protein dan albumin
- Enzim hati: SGPT, SGOT, Alkaline Phosphotase
- Rasio albumin/globulin
 
## 🤖 Model Machine Learning
 
Model yang digunakan adalah **XGBoost Classifier** dengan pipeline yang mencakup:
 
1. **Eksplorasi Data (EDA)** — analisis distribusi, missing values, dan korelasi fitur
2. **Preprocessing** — encoding kategorikal, imputasi missing values, scaling fitur
3. **Pelatihan Model** — XGBoost dengan tuning hyperparameter
4. **Evaluasi** — akurasi, precision, recall, F1-score, dan confusion matrix
5. **Penyimpanan Model** — model disimpan menggunakan `joblib` untuk dipakai di aplikasi

## 🌐 Demo Aplikasi
👉 [https://liver-disease-predict.streamlit.app/](https://liver-disease-predict.streamlit.app/)
