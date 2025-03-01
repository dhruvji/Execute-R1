import requests
import json

url = "http://127.0.0.1:8000/execute"

payload = {
  "code": "R = 3\nC = 3\ndef min_cost(cost, m, n):\n    tc = [[0 for x in range(C)] for x in range(R)]\n    tc[0][0] = cost[0][0]\n    for i in range(1, m+1):\n        tc[i][0] = tc[i-1][0] + cost[i][0]\n    for j in range(1, n+1):\n        tc[0][j] = tc[0][j-1] + cost[0][j]\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            tc[i][j] = min(tc[i-1][j-1], tc[i-1][j], tc[i][j-1]) + cost[i][j]\n    return tc[m][n]",
  "test_cases": [
    "assert min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) == 8",
    "assert min_cost([[2, 3, 4], [5, 9, 3], [2, 6, 4]], 2, 2) == 12",
    "assert min_cost([[3, 4, 5], [6, 10, 4], [3, 7, 5]], 2, 2) == 16"
  ]
}


headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(response.json().get("test_results"))  
print(response.json().get("error"))  

