from typing import Any, NotRequired, TypedDict
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


class BodiesType(TypedDict):
    json: NotRequired[str]
    form: NotRequired[str]


def extract_request_body(body: dict[str, Any]) -> BodiesType:
    content = body["content"]
    json = content.get("application/json")
    form = content.get("application/x-www-form-urlencoded")
    # multipart = content.get("multipart/form-data")

    def extract_body_name(field: dict[str, Any]):
        ref: str = field["schema"]["$ref"]
        last_slash = ref.rfind("/")
        return ref[last_slash + 1 :]

    bodies: BodiesType = {}

    if json:
        # For some reason datamode-codegen will convert snake_case from openapi.json to camelCase name of python classes
        # So mimick this, otherwise, in stub file, we cannot import generated classes.
        bodies["json"] = extract_body_name(json)
    if form:
        bodies["form"] = extract_body_name(form)

    return bodies


class Route(TypedDict):
    response_model: str
    http_route: str
    http_method: str
    unique: bool
    json_body: NotRequired[str]
    form_body: NotRequired[str]


routes: list[Route] = []
models_to_import: set[str] = set()  # a 'set' class to avoid duplicates
method_count: dict[str, int] = {}

for path in all_paths:
    for method in all_paths[path]:
        route: dict[str, Any] = all_paths[path][method]  # current route considered

        model = extract_successful_response(route["responses"])
        if model != "None":
            models_to_import.add(model)

        if method not in method_count:
            method_count[method] = 1
        else:
            method_count[method] += 1

        route_data: Route = {"response_model": model, "http_route": path, "http_method": method, "unique": False}
        # if this is a POST route, we also add type for the request body
        if method == "post" and "requestBody" in route:
            request_body = extract_request_body(route["requestBody"])
            if "json" in request_body:
                route_data["json_body"] = request_body["json"]
                models_to_import.add(request_body["json"])

            if "form" in request_body:
                route_data["form_body"] = request_body["form"]
                models_to_import.add(request_body["form"])

        routes.append(route_data)

for one_route in routes:
    # If our API, say, has only one PUT route, we would render '@overload' for a unique method definition which is type error.
    # The 'unique' is used in Jinja template to not render '@overload' in that case
    if method_count[one_route["http_method"]] == 1:
        one_route["unique"] = True

# Now let's load Jinja template file and render our stub file
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./tests/test_client/"))
template = environment.get_template("api_stub.py.jinja2")
rendered = template.render(routes=routes, models_to_import=list(models_to_import))

with open("./tests/test_client/__init__.pyi", mode="w", encoding="utf-8") as message:
    message.write(rendered)
