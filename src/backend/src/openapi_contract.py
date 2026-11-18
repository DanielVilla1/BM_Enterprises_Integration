# ===== AI GENERATED: install_openapi_contract =====
# Purpose: Describe the actual RFC 9457 validation response independently of Python HTTP reason phrases.
# Inputs: The assembled FastAPI application.
# Returns: Stable error descriptions and the actual problem+json response schema.
# Flow: Delegate schema generation, then annotate documented error responses.

from fastapi import FastAPI


def install_openapi_contract(application: FastAPI) -> None:
    original_openapi = application.openapi

    def canonical_openapi() -> dict[str, object]:
        schema = original_openapi()
        for operations in schema.get("paths", {}).values():
            for operation in operations.values():
                if not isinstance(operation, dict):
                    continue
                for code, response in operation.get("responses", {}).items():
                    if not code.isdigit() or int(code) < 400:
                        continue
                    descriptions = {
                        "413": "Payload too large",
                        "414": "URI too long",
                        "422": "Validation failed",
                    }
                    if code in descriptions:
                        response["description"] = descriptions[code]
                    response["content"] = {
                        "application/problem+json": {
                            "schema": {"$ref": "#/components/schemas/ProblemDetailsResponse"}
                        }
                    }
        return schema

    application.openapi = canonical_openapi
