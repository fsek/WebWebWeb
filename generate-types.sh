# Launch our server in background so that it makes the openapi.json file available.
# From openapi.json, datamodel-codegen reads what field and types our objects have and creates TypedDicts from them.

uvicorn main:app & # launch in background
sleep 4 # give it some time to start
process_id=$!
echo "Started server to read OpenAPI schema. Process id: $process_id"

datamodel-codegen --input-file-type openapi --url http://localhost:8000/openapi.json \
  --output ./tests/test_client/generated_types.py --target-python-version 3.11 --use-annotated \
   --enum-field-as-literal all  --output-model-type typing.TypedDict

python ./tests/test_client/generate_api_stub.py

# Close server background process
kill $process_id
wait
echo "Types generated!"