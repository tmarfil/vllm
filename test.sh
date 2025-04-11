curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "messages": [
      {"role": "user", "content": "Write a simple F5 iRule that redirects HTTP traffic to HTTPS"}
    ],
    "temperature": 0.7
  }' | jq -r '.choices[0].message.content'
