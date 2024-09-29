from typing import Any, TypedDict
import jinja2
import requests

# For this file, we assume we have a server running
# To read our OpenAPI schema, we make a GET request to /openapi.json
res = requests.get("http://127.0.0.1:8000/openapi.json")
api: dict[str, Any] = res.json()
all_paths: dict[str, dict[str, Any]] = api["paths"]


# To best see what happens, look at /openapi.json which is served by server when it's running
def extract_successful_response(responses: dict[str, Any]) -> str:
    success_codes = [x for x in responses.keys() if x[0:1] == "2"]  # catch all 200-299 status codes
    if len(success_codes) > 1:
        raise Exception(
            "Encountered more than 1 2XX response. Let's only have at most one possible success response from a route, to make things simpler"
        )
    if len(success_codes) == 0:
        raise Exception("No successful responses could be found in openapi.json for this route")

    resp = responses[str(success_codes[0])]
    if "content" not in resp:
        # Happens in 204 responses, for example
        return "None"
    schema = resp["content"]["application/json"]["schema"]
    ref: str
    if "type" in schema and schema["type"] == "array":
        ref = schema["items"]["$ref"]
    elif "$ref" in schema:
        ref = schema["$ref"]
    else:
        # This status code may have an empty response
        return "None"
    last_slash = ref.rfind("/")
    model = ref[last_slash + 1 :]
    return model


class Route(TypedDict):
    response_model: str
    http_route: str
    http_method: str
    unique: bool


routes: list[Route] = []
models_to_import: set[str] = set()  # a 'set' class to avoid duplicates
method_count: dict[str, int] = {}

for path in all_paths:
    for method in all_paths[path]:
        responses = all_paths[path][method]["responses"]
        model = extract_successful_response(responses)
        if model != "None":
            models_to_import.add(model)

        if method not in method_count:
            method_count[method] = 1
        else:
            method_count[method] += 1
        routes.append({"response_model": model, "http_route": path, "http_method": method, "unique": False})

for route in routes:
    # If our API, say, has only one PUT route, we would render '@overload' for a unique method definition.
    # The 'unique' is used in Jinja template to not render '@overload' in that case
    if method_count[route["http_method"]] == 1:
        route["unique"] = True

# Now let's load Jinja template file and render our stub file
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./tests/test_client/"))
template = environment.get_template("api_stub.jinja")
rendered = template.render(routes=routes, models_to_import=list(models_to_import))

with open("./tests/test_client/__init__.pyi", mode="w", encoding="utf-8") as message:
    message.write(rendered)
