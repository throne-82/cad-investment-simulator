from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SimulationRequest(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        allow_inf_nan=False,
    )

    initial_principal: float = Field(ge=0, le=10_000_000)
    monthly_contribution: float = Field(ge=0, le=100_000)
    annual_rate: float = Field(ge=0, le=1)
    years: int = Field(ge=1, le=60)


class AnnualResult(BaseModel):
    year: int
    total_contributions: str
    interest: str
    final_balance: str


class SimulationResponse(BaseModel):
    currency: Literal["CAD"] = "CAD"
    total_contributions: str
    interest: str
    final_balance: str
    annual_progression: list[AnnualResult]
