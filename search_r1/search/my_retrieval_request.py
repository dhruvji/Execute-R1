import requests
url = "http://127.0.0.1:8000/execute"
payload = {
        "code": "print('Hello!')", 
        "test_cases": []

        }
response = requests.post(url, json=payload)
response.raise_for_status()
retrieved_data = response.json()
print("Response from server:")
print(retrieved_data)

