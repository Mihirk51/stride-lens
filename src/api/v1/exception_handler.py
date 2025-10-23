from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Custom handler for Pydantic ValidationError to return clean error messages.
    """
    errors = []
    for error in exc.errors():
        if error["type"] == "value_error":
            errors.append(error["msg"])
        else:
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed",
            "messages": errors,
        },
    )
