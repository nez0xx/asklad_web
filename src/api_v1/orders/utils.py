import os
from datetime import datetime

import httpx
from fastapi import UploadFile, HTTPException, status

from src.core.settings import BASE_DIR, settings
from src.parser import parse


async def parse_excel(file: UploadFile, ):
    content = await file.read()
    date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{date}_{file.filename}"
    full_filename = os.path.join(BASE_DIR, 'uploaded_files', filename)

    with open(full_filename, "wb") as f:
        f.write(content)

    # json объекты
    try:
        united_orders = parse(full_filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File parsing error: {e}"
        )

    return united_orders
