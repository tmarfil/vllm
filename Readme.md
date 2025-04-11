# vLLM Multi-GPU Setup Guide

This guide walks through setting up and using vLLM with multiple GPUs to serve large language models efficiently.

## Prerequisites

- CUDA-compatible GPUs (this guide uses 2x RTX 3090 Ti)
- Ubuntu/Linux system
- Python 3.10+
- CUDA drivers properly installed
- Hugging Face account (for accessing gated models)

## Installation

### 1. Create a project directory and virtual environment

```bash
# Create project directory
mkdir -p ~/projects/vllm
cd ~/projects/vllm

# Create and activate virtual environment with UV
uv venv .venv
source .venv/bin/activate
```

### 2. Install vLLM

```bash
# Install vLLM
uv pip install vllm
```

### 3. Verify GPU detection

Ensure your GPUs are properly detected:

```bash
nvidia-smi
```

You should see output showing all available GPUs, their memory, utilization, etc.

## Authentication for Gated Models

Many models on Hugging Face require authentication to download. Follow these steps:

1. Create a Hugging Face account at [huggingface.co](https://huggingface.co) if you don't have one
2. Accept the model terms on the model's page (e.g., [google/gemma-3-27b-it](https://huggingface.co/google/gemma-3-27b-it))
3. Create a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) with "Read access to contents of all public gated repos you can access"
4. Set up authentication:

```bash
# Export token (temporary)
export HF_TOKEN=your_token_here

# Login with Hugging Face CLI (persistent)
pip install huggingface_hub
huggingface-cli login --token $HF_TOKEN
```

## Serving Models

### Basic Model Serving

To serve a model with vLLM across multiple GPUs:

```bash
vllm serve "MODEL_NAME" --tensor-parallel-size 2
```

### Optimized Model Serving

For optimal performance, especially with larger models:

```bash
vllm serve "MODEL_NAME" --tensor-parallel-size 2 --gpu-memory-utilization 0.95 --swap-space 16 --max-model-len 8192
```

Parameters explained:
- `--tensor-parallel-size 2`: Splits the model across 2 GPUs
- `--gpu-memory-utilization 0.95`: Uses 95% of available GPU memory
- `--swap-space 16`: Allocates 16GB of system RAM as swap space
- `--max-model-len 8192`: Sets maximum context window to 8K tokens

## Model Examples

Here are some examples of running different models:

### Multimodal Model (7B)

```bash
vllm serve "Qwen/Qwen2.5-VL-7B-Instruct" --tensor-parallel-size 2 --gpu-memory-utilization 0.95 --swap-space 16 --max-model-len 8192
```

### Code Model (7B)

```bash
vllm serve "Qwen/Qwen2.5-Coder-7B-Instruct" --tensor-parallel-size 2 --gpu-memory-utilization 0.95 --swap-space 16 --max-model-len 8192
```

## Testing the API

Once your model is running, you can test it with curl or Python requests.

### Using curl

Create a file named `test.sh` with the following content:

```bash
#!/bin/bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [
      {"role": "user", "content": "Write a simple F5 iRule that redirects HTTP traffic to HTTPS"}
    ],
    "temperature": 0.7
  }' | jq
```

Make it executable and run:

```bash
chmod +x test.sh
./test.sh
```

For pretty-printing just the model response:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [
      {"role": "user", "content": "Write a simple F5 iRule that redirects HTTP traffic to HTTPS"}
    ],
    "temperature": 0.7
  }' | jq -r '.choices[0].message.content'
```

### Using Python

Create a file named `test.py` with:

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "Qwen/Qwen2.5-VL-7B-Instruct",
        "messages": [
            {"role": "user", "content": "Write a simple F5 iRule that redirects HTTP traffic to HTTPS"}
        ],
        "temperature": 0.7
    }
)

# Pretty print the entire response
print(json.dumps(response.json(), indent=2))

# Or just print the content
print("\nJust the response content:")
print(response.json()['choices[0]['message']['content'])
```

Run it:

```bash
python test.py
```

## Running in Background

To run the server in the background:

```bash
nohup vllm serve "MODEL_NAME" --tensor-parallel-size 2 --gpu-memory-utilization 0.95 --swap-space 16 --max-model-len 8192 > vllm.log 2>&1 &
```

Check logs:

```bash
tail -f vllm.log
```

## Troubleshooting

### Memory Issues

If you encounter "No available memory for the cache blocks" or similar errors:
- Reduce `--max-model-len` to a smaller value (e.g., 4096)
- Lower `--gpu-memory-utilization` (e.g., 0.85)
- Increase `--swap-space` if you have available system RAM
- Try a quantized model version (e.g., with `--quantization awq`)

### NVIDIA Driver Issues

If `nvidia-smi` fails:
```bash
sudo apt update
sudo apt install linux-headers-$(uname -r)
sudo apt install nvidia-driver-XXX  # Replace XXX with appropriate version
sudo reboot
```

### Authentication Issues

For "Cannot access gated repo" errors:
- Verify you've accepted the model terms on Hugging Face
- Check that your token has the correct permissions
- Ensure you're properly logged in with `huggingface-cli login`

### Resources

- [vLLM Documentation](https://docs.vllm.ai/)
- [vLLM GitHub Repository](https://github.com/vllm-project/vllm)
- [Hugging Face Models](https://huggingface.co/models)

### Disk Usage

```bash
du -sh ~/.cache/huggingface/hub/
```
