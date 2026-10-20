import json
import os
import subprocess
import sys
from pathlib import Path

config = json.loads(os.environ["AZURE_CONFIG"])
registry = config["registry_login_server"]
commit = os.environ["GITHUB_SHA"]

local_directory = Path(".local")
local_directory.mkdir(exist_ok=True)

backend_settings = {
    "resource_group_name": config["state_resource_group_name"],
    "storage_account_name": config["state_storage_account_name"],
    "container_name": "application",
    "key": "application.tfstate",
}

backend_lines = [
    f"{key} = {json.dumps(value)}" for key, value in backend_settings.items()
]
backend_lines.append("use_azuread_auth = true")

(local_directory / "application.backend.hcl").write_text(
    "\n".join(backend_lines) + "\n"
)

variables = {"config": config}

for service in ("backend", "frontend"):
    image = f"{registry}/{service}:{commit}"

    if "--digests" in sys.argv:
        image = subprocess.check_output(
            [
                "docker",
                "image",
                "inspect",
                "--format",
                "{{index .RepoDigests 0}}",
                image,
            ],
            text=True,
        ).strip()

        if "@sha256:" not in image:
            raise ValueError("Expected an immutable image digest")

    variables[f"{service}_image"] = image
    print(f"{service} image: {image}")

(local_directory / "application.tfvars.json").write_text(
    json.dumps(variables, indent=2) + "\n"
)

with Path(os.environ["GITHUB_ENV"]).open("a") as environment:
    environment.write(f"ACR_NAME={config['registry_name']}\n")
    environment.write(f"REGISTRY={registry}\n")
