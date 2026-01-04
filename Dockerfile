# Gunakan image Python yang ringan
FROM python:3.10-slim

# Install library sistem untuk OpenCV dan YOLO
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set direktori kerja
WORKDIR /app

# Copy file requirements dulu agar proses build cepat (caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project (termasuk api.py dan best.pt)
COPY . .

# Expose port yang digunakan FastAPI
EXPOSE 8000

# Ubah baris terakhir menjadi ini:
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
