import requests

url = "http://127.0.0.1:8000/execute"
payload = {"code": "print('hello')"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(response.json())  # Output: {'output': '4\n', 'error': None}
