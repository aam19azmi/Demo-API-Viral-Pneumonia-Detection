# Gunakan image Python yang ringan
FROM python:3.10-slim

# Install library sistem untuk OpenCV yang kompatibel dengan Debian terbaru
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set direktori kerja
WORKDIR /app

# Copy file requirements dulu agar proses build cepat (caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project
COPY . .

# Expose port yang digunakan FastAPI
EXPOSE 8000

# Jalankan API menggunakan uvicorn (pastikan api:app tanpa .py)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
