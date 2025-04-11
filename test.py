import requests
import json

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "messages": [
            {"role": "user", "content": "Write a simple F5 iRule that redirects HTTP traffic to HTTPS"}
        ],
        "temperature": 0.7
    }
)

# Pretty print the entire response
print(json.dumps(response.json(), indent=2))
