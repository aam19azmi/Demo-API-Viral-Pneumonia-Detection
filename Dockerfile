FROM python:3.10-slim

# Install library minimal
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install torch CPU dulu baru yang lain untuk menghemat space
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch torchvision
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hapus file yang tidak perlu jika ada (opsional)
RUN rm -rf /root/.cache/pip

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
