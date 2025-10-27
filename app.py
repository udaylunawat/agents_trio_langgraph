from fastapi import FastAPI
from agents.aqi import AQIQuery, answer_aqi
from agents.pdfs import PDFQuery, answer_pdf
from agents.youtube import YTRequest, recommend_next

app = FastAPI(title="Plan A — Micro Agents (AQI / PDFs / YouTube)")

@app.get("/")
def root():
    return {"ok": True, "routes": ["/docs", "/aqi/query", "/pdfs/query", "/youtube/recommend"]}

@app.post("/aqi/query")
def aqi(q: AQIQuery):
    return answer_aqi(q)

@app.post("/pdfs/query")
def pdfs(q: PDFQuery):
    return answer_pdf(q)

@app.post("/youtube/recommend")
def youtube(q: YTRequest):
    return recommend_next(q)
