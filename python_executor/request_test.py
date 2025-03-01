import requests
import json

# API endpoint
url = "http://127.0.0.1:8000/execute"

# Input file containing JSON lines
input_file = "mbpp_data.jsonl"
# Output file to store results
output_file = "output_results.json"

# List to store test results
results = []

# Read and process each JSON line
with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        try:
            # Parse the JSON line
            data = json.loads(line.strip())

            # Prepare the payload for the API request
            payload = {
                "code": data["code"],
                "test_cases": data["test_list"]
            }

            headers = {"Content-Type": "application/json"}

            # Send request to FastAPI server
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()

            # Format the output entry
            output_entry = {
                "task_id": data["task_id"],
                "text": data["text"],
                "test_results": result.get("test_results", []),
                "error": result.get("error")
            }

            # Save result in the list
            results.append(output_entry)

            print(f"Task {data['task_id']} processed.")
            print(f"Output: {output_entry}")

        except json.JSONDecodeError:
            print(f"Invalid JSON format in line: {line}")
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")

# Write results to an output JSON file
with open(output_file, "w", encoding="utf-8") as outfile:
    json.dump(results, outfile, indent=2)

print(f"Results saved in {output_file}")
