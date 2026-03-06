from fastapi import FastAPI, UploadFile
from PIL import Image
from fastapi.responses import StreamingResponse
from io import BytesIO
from pathlib import Path
from rembg import remove
import pymupdf 
import os
import zipfile
from pdf2docx import Converter


 
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
    
@app.post("/remove-bg")

async def remove_background(file: UploadFile):
    
    if (file.content_type).find('image') != -1:
        contents = await file.read()
        img = Image.open(BytesIO(contents))
        
  
        removed_bg = remove(img)
        out_img_format = 'PNG'
        img_name = Path(file.filename).stem
        output_buffer = BytesIO()

        removed_bg.save(output_buffer, format=out_img_format.upper())
        output_buffer.seek(0)

        return StreamingResponse(
            output_buffer,
            media_type=f"image/{out_img_format.lower()}",
            headers={"Content-Disposition": f"attachment; filename={img_name}_nobg.{out_img_format.lower()}"}
        )

    else:
        return {'message':'file is not an image'}

@app.post("/pdf2img")

async def convert_pdf_to_img(file: UploadFile):
    
    if file.content_type == 'application/pdf':
        contents = await file.read()
        user_file = pymupdf.open(stream=contents, filetype="pdf")

        base_name = Path(file.filename).stem

        for page_num in range(user_file.page_count):

            page = user_file[page_num]
        
        pix = page.get_pixmap()

        if user_file.page_count == 1:
            page = user_file[0]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            output_buffer = BytesIO(img_bytes)
            output_buffer.seek(0)
            return StreamingResponse(
                output_buffer,
                media_type="image/png",
                headers={"Content-Disposition": f"attachment; filename={base_name}.png"}
            )
        else:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for page_num in range(user_file.page_count):
                    page = user_file[page_num]
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    zip_file.writestr(f"{base_name}_page{page_num + 1}.png", img_bytes)
            zip_buffer.seek(0)
            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={base_name}_pages.zip"}
            )
        
      
    else:
        return{'message':'File is not a pdf'}
    
# @app.post("/pdf2docx")

# async def convert_pdf_to_docx(file: UploadFile):
    
#     if file.content_type == 'application/pdf':
#         contents = await file.read()
#         user_file = pymupdf.open(stream=contents, filetype="pdf")

#         base_name = Path(file.filename).stem

#         pdf_converter = Converter(user_file)
#         pdf_converter.convert()

       
      
#     else:
#         return{'message':'File is not a pdf'}



