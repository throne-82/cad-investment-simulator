import http from "k6/http";
import { check } from "k6";

export const options = {
  vus: 2,
  stages: [
    { duration: "30s", target: 2 },
    { duration: "30s", target: 20 },
    { duration: "1m", target: 100 },
    { duration: "2m", target: 100 },
    { duration: "30s", target: 2 },
    { duration: "1m", target: 2 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
    checks: ["rate>0.99"],
  },
};

export default function () {
  const payload = {
    initial_principal: Math.round(1000 + Math.random() * 100000),
    monthly_contribution: Math.round(100 + Math.random() * 500),
    annual_rate: 0.03 + Math.random() * 0.07,
    years: 1 + Math.floor(Math.random() * 60),
  };

  const response = http.post(
    `${__ENV.BASE_URL}/api/simulate`,
    JSON.stringify(payload),
    {
      headers: { "Content-Type": "application/json" },
      timeout: "10s",
    },
  );

  check(response, {
    "status is 200": (r) => r.status === 200,
    "annual progression matches duration": (r) =>
      r.status === 200 &&
      r.json("annual_progression").length === payload.years,
  });
}
