from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from predict import predict_dicom
import tempfile
import base64
import pydicom
import matplotlib.pyplot as plt
import io

app = FastAPI()

# CORS settings for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dcm") as tmp_file:
            tmp_file.write(contents)
            tmp_path = tmp_file.name

        # Use updated rule-based classifier
        label, confidence = predict_dicom(tmp_path)

        # Convert to PNG for display
        dicom = pydicom.dcmread(tmp_path)
        image = dicom.pixel_array
        fig, ax = plt.subplots()
        ax.imshow(image, cmap="gray")
        ax.axis("off")
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        encoded_img = base64.b64encode(buf.getvalue()).decode("utf-8")

        return JSONResponse(content={
            "label": label,
            "confidence": f"{confidence*100:.2f}%",
            "image": encoded_img
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
