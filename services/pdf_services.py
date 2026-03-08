from fastapi.responses import StreamingResponse
from io import BytesIO
from pathlib import Path
import pymupdf
import zipfile

async def pdf_to_img(file):
    if file.content_type != 'application/pdf':
        return {'message': 'File is not a pdf'}

    contents = await file.read()
    user_file = pymupdf.open(stream=contents, filetype="pdf")
    base_name = Path(file.filename).stem

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