from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from ultralytics import YOLO
import uvicorn
from PIL import Image
import io
import os

app = FastAPI(title="Pneumonia Detection API - AzmiDev")

# --- LOAD MODEL ---
# Railway akan mencari file ini di root folder
MODEL_PATH = "best.pt"
model = YOLO(MODEL_PATH)

# --- SECURITY ---
# Ambil API Key dari environment variable Railway (kita set nanti)
# Jika tidak ada di environment, gunakan default 'AzmiHealthAI_Secret'
API_KEY_SECRET = os.getenv("API_KEY_SECRET", "AzmiHealthAI_Secret")

@app.get("/")
def home():
    return {"status": "online", "message": "Pneumonia Detection API is running"}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...), 
    x_api_key: str = Header(None) # n8n harus mengirim header 'x-api-key'
):
    # Validasi API Key
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Akses ditolak: API Key salah.")

    try:
        # Membaca gambar
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Jalankan Inferensi
        # conf=0.4 untuk keseimbangan antara presisi dan recall
        results = model.predict(img, conf=0.4)
        
        detections = []
        for box in results[0].boxes:
            detections.append({
                "label": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "box": box.xyxy[0].tolist() # Koordinat bounding box jika n8n butuh
            })
        
        # --- Logika Hasil Baru ---
        # Kita cek apakah ada label 'PNEUMONIA' di dalam daftar deteksi
        has_pneumonia = any(d['label'].upper() == 'PNEUMONIA' for d in detections)
        
        if has_pneumonia:
            message = "Indikasi Pneumonia Terdeteksi. Segera konsultasikan ke dokter."
        elif len(detections) > 0:
            message = "Hasil Analisis: Paru-paru dalam kondisi NORMAL."
        else:
            message = "Tidak ada objek yang terdeteksi. Pastikan gambar adalah foto X-Ray dada."
        
        return {
            "status": "success",
            "results_count": len(detections),
            "is_pneumonia": has_pneumonia,
            "message": message,
            "detections": detections,
            "model_version": "YOLOv8s-GWO-V1"
        }
    
    except Exception as e:
        return {"status": "error", "message": f"Terjadi kesalahan: {str(e)}"}

if __name__ == "__main__":
    # Railway membutuhkan port yang dinamis, diambil dari environment variable PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    