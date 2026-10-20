from decimal import ROUND_HALF_UP, Decimal, localcontext

from .models import AnnualResult, SimulationRequest, SimulationResponse


def format_money(value: Decimal) -> str:
    rounded = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(rounded, ".2f")


def simulate(data: SimulationRequest) -> SimulationResponse:
    with localcontext() as context:
        context.prec = 40

        principal = Decimal(str(data.initial_principal))
        contribution = Decimal(str(data.monthly_contribution))
        annual_rate = Decimal(str(data.annual_rate))

        monthly_rate = (Decimal(1) + annual_rate) ** (
            Decimal(1) / Decimal(12)
        ) - Decimal(1)

        balance = principal
        annual_results = []

        for month in range(1, data.years * 12 + 1):
            balance *= Decimal(1) + monthly_rate
            balance += contribution

            if month % 12 == 0:
                total_contribuitions = principal + contribution * month
                interest = balance - total_contribuitions

                annual_results.append(
                    AnnualResult(
                        year=month // 12,
                        total_contributions=format_money(total_contribuitions),
                        interest=format_money(interest),
                        final_balance=format_money(balance),
                    )
                )
        final_year = annual_results[-1]

        return SimulationResponse(
            total_contributions=final_year.total_contributions,
            interest=final_year.interest,
            final_balance=final_year.final_balance,
            annual_progression=annual_results,
        )
