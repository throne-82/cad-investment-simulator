from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .calculator import simulate
from .models import SimulationRequest, SimulationResponse

app = FastAPI(title="CAD Investment Simulator", version="0.1.0")


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
