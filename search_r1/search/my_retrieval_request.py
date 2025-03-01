import requests
url = "http://127.0.0.1:8000/execute"
payload = {
        "code": ["print('Hello!')", "goomba", "print('Hello2')\nx=2\nprint(x)"], 
        "test_cases": [['assert True', 'assert 0 == 2'], ['assert False'], ['assert True']]
        }
response = requests.post(url, json=payload)
response.raise_for_status()
retrieved_data = response.json()
print("Response from server:")
print(retrieved_data)

