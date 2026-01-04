from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from ultralytics import YOLO
import uvicorn
from PIL import Image
import io
import os
from fastapi.responses import StreamingResponse
import json

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
    redirect_url = "https://demo-viral-pneumonia-detection-dpagyfkt9pyxbz2svfgxsd.streamlit.app/"
    return {"redirect_url": redirect_url}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...), 
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 1. Jalankan Inferensi
        results = model.predict(img, conf=0.4)
        
        # 2. Ambil data deteksi untuk Logika
        detections = []
        for box in results[0].boxes:
            detections.append({
                "label": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0])
            })
        
        has_pneumonia = any(d['label'].upper() == 'PNEUMONIA' for d in detections)
        message = "Indikasi Pneumonia Terdeteksi" if has_pneumonia else "Normal"

        # 3. Plot gambar (Bounding Boxes)
        res_plotted = results[0].plot() # Menghasilkan array gambar dengan kotak
        img_res = Image.fromarray(res_plotted)

        # 4. Simpan gambar hasil deteksi ke memory buffer
        buf = io.BytesIO()
        img_res.save(buf, format="JPEG")
        buf.seek(0)

        # 5. Bungkus data JSON ke dalam string untuk dikirim via Header
        result_data = {
            "is_pneumonia": has_pneumonia,
            "message": message,
            "label": detections[0]['label'] if detections else "N/A",
            "confidence": detections[0]['confidence'] if detections else 0
        }

        # Mengembalikan File Gambar + Data JSON di Header 'x-result'
        return StreamingResponse(
            buf, 
            media_type="image/jpeg",
            headers={"x-result": json.dumps(result_data)}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    