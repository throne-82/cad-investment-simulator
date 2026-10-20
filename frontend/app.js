const form = document.querySelector("#simulation-form");
const button = form.querySelector("button");
const status = document.querySelector("#status");
const results = document.querySelector("#results");

const money = new Intl.NumberFormat("en-CA", {
  style: "currency",
  currency: "CAD",
  currencyDisplay: "code",
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  button.disabled = true;
  results.hidden = true;
  status.textContent = "Calculating...";

  const fields = form.elements;
  const payload = {
    initial_principal: Number(fields.initial_principal.value),
    monthly_contribution: Number(fields.monthly_contribution.value),
    annual_rate: Number(fields.annual_rate_percent.value) / 100,
    years: Number(fields.years.value),
  };

  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(15000),
    });

    if (!response.ok) {
      status.textContent = response.status === 422
        ? "Check the input values and try again."
        : "The simulation service is temporarily unavailable.";
      return;
    }

    const data = await response.json();

    document.querySelector("#contributions").textContent =
      money.format(data.total_contributions);
    document.querySelector("#interest").textContent =
      money.format(data.interest);
    document.querySelector("#balance").textContent =
      money.format(data.final_balance);

    const rows = data.annual_progression.map((year) => {
      const row = document.createElement("tr");
      const values = [
        year.year,
        money.format(year.total_contributions),
        money.format(year.interest),
        money.format(year.final_balance),
      ];

      for (const value of values) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      }

      return row;
    });

    document.querySelector("#annual-results").replaceChildren(...rows);
    results.hidden = false;
    status.textContent = "Simulation complete.";
  } catch {
    status.textContent =
      "Unable to reach the simulation service. Please try again.";
  } finally {
    button.disabled = false;
  }
});