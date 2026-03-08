from fastapi import FastAPI
from routers import images, pdf

app = FastAPI()

app.include_router(images.router)
app.include_router(pdf.router)

@app.get("/")
async def root():
    return {"message": "Root"}