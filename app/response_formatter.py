from typing import Any, Optional

from fastapi.responses import JSONResponse


async def send_api_response(
    message: str,
    success: bool = True,
    data: Optional[Any] = None,
    status_code: Optional[int] = None,
):
    return JSONResponse(
        {
            "message": message,
            "success": success,
            "data": data,
        },
        status_code if status_code else 200 if success else 500,
    )
