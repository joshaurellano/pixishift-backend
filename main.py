from fastapi import FastAPI
from routers import images_routes, pdf_routes

app = FastAPI()

app.include_router(images_routes.router)
app.include_router(pdf_routes.router)

@app.get("/")
async def root():
    return {"message": "Root"}