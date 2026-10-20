import json
import logging
import re
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .calculator import simulate
from .models import SimulationRequest, SimulationResponse

app = FastAPI(title="CAD Investment Simulator", version="0.1.0")
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("cad.requests")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    incoming_id = request.headers.get("X-Request-ID", "")
    request_id = (
        incoming_id if re.fullmatch(r"[0-9a-fA-F-]{1,36}", incoming_id) else uuid4().hex
    )
    started = perf_counter()
    status = 500

    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        route = getattr(request.scope.get("route"), "path", "unmatched")

        if route != "/api/health":
            logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "route": route,
                        "status": status,
                        "duration_ms": round((perf_counter() - started) * 1000, 2),
                        "request_id": request_id,
                    }
                )
            )


@app.exception_handler(RequestValidationError)
async def validation_error(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/simulate", response_model=SimulationResponse)
def simulate_investment(data: SimulationRequest) -> SimulationResponse:
    return simulate(data)
