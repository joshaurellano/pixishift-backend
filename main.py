from fastapi import FastAPI, UploadFile
from PIL import Image
from fastapi.responses import StreamingResponse
from io import BytesIO
from pathlib import Path

 
app = FastAPI()

@app.get("/")
async def root():
    return{"message":"Root"}


@app.post("/convert")

async def create_upload_file(
        file: UploadFile,
        out_img_format: str):
    
    image_format = ['PNG', 'WEBP', 'JPG', 'JPEG', 'AVIF', 'BMP', 'TIFF']

    
    if (file.content_type).find('image') != -1:
        contents = await file.read()
        img = Image.open(BytesIO(contents))
        
        if out_img_format.upper() not in image_format:
            return {'message':'Desired output is not accepted'}
        if out_img_format.upper() == img.format.upper():
            return {'message':'Desired output should not be the same as original'}
        if out_img_format.upper() in ('JPEG', 'JPG', 'BMP'):
            if img.mode != 'RGB':
                img = img.convert('RGB')
        if out_img_format.upper() == 'JPG':
            out_img_format = 'JPEG'

        img_name = Path(file.filename).stem
        output_buffer = BytesIO()

        img.save(output_buffer, format=out_img_format.upper())
        output_buffer.seek(0)

        return StreamingResponse(
            output_buffer,
            media_type=f"image/{out_img_format.lower()}",
            headers={"Content-Disposition": f"attachment; filename={img_name}_converted.{out_img_format.lower()}"}
        )

    else:
        return {'message':'file is not an image'}
    
    


