# X-ONE Advanced Configuration

Deep dive into Ollama optimization, GPU setup, and performance tuning.

## Ollama Configuration

### Environment Variables

```bash
# Base URL (default: http://localhost:11434)
export OLLAMA_URL=http://localhost:11434

# Model to use (default: dolphin-llama3)
export OLLAMA_MODEL=dolphin-llama3

# API Server Port
export OLLAMA_PORT=11434

# Number of GPU layers to use
export OLLAMA_NUM_GPU=1

# CPU threads (default: auto-detect)
export OLLAMA_NUM_THREAD=8

# Maximum context tokens
export OLLAMA_CONTEXT_SIZE=2048

# Memory per model (in MB)
export OLLAMA_MEMORY=8192
```

### Ollama Options String

Set via environment or `.env`:

```bash
export OLLAMA_OPTS="
  --num-gpu 1 
  --num-thread 16
  --context-size 2048
  --keep-alive 5m
"
```

### Model-Specific Options

In `.env`, set per-model parameters:

```bash
# For GPU model (dolphin-llama3)
OLLAMA_MODEL=dolphin-llama3
OLLAMA_OPTS="--num-gpu 1 --num-thread 8"

# For fast CPU model
OLLAMA_MODEL=llama3.2:1b
OLLAMA_OPTS="--num-gpu 0 --num-thread 16"
```

---

## GPU Setup

### NVIDIA CUDA

#### Prerequisites
```bash
# Check NVIDIA GPU
nvidia-smi

# Output should show:
# | NVIDIA-SMI 535.104.05 | Driver Version: 535.104.05 | CUDA Version: 12.2 |
```

#### Install CUDA Toolkit

**Ubuntu/Debian:**
```bash
# Add CUDA repo
curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb \
  -o cuda-keyring.deb
sudo dpkg -i cuda-keyring.deb

# Install
sudo apt update
sudo apt install cuda-toolkit
```

**Verify installation:**
```bash
nvcc --version
# Output: nvcc: NVIDIA (R) Cuda compiler driver

nvidia-smi
```

#### Configure Ollama for CUDA

1. Stop Ollama:
```bash
sudo systemctl stop ollama
```

2. Set environment:
```bash
export CUDA_VISIBLE_DEVICES=0  # Use GPU 0
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export PATH=/usr/local/cuda/bin:$PATH
```

3. Start Ollama:
```bash
sudo systemctl start ollama

# Or run directly
ollama serve
```

4. Verify GPU usage:
```bash
nvidia-smi  # Should show Ollama process under GPU utilization
ollama ps   # Should show model loaded
```

#### Test Performance

```bash
# Time a single request
time curl -X POST http://localhost:11434/api/generate \
  -d '{
    "model": "dolphin-llama3",
    "prompt": "List 5 ways to test SQL injection",
    "stream": false
  }' | jq '.response' | wc -c
```

**Expected timings:**
- With GPU: ~2-4 seconds for 100 tokens
- Without GPU: ~30-60 seconds for 100 tokens

### AMD ROCm (Radeon GPU)

```bash
# Install ROCm
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo "deb [arch=amd64] https://repo.radeon.com/rocm/apt/debian focal main" | sudo tee -a /etc/apt/sources.list.d/rocm.list
sudo apt update
sudo apt install rocm-dkms

# Set environment
export HSA_OVERRIDE_GFX_VERSION=gfx906  # AMD RX 5700 XT (check your GPU)
export OLLAMA_NUM_GPU=1

# Start Ollama
ollama serve
```

### Apple Metal (M1/M2/M3)

Automatically enabled on macOS with Ollama. No additional setup needed.

```bash
# Verify Metal GPU usage
ollama ps
# Should show GPU acceleration active
```

---

## Performance Optimization

### Speed vs Quality Trade-off

#### Fast Response (Pentesting Speed)
```bash
# .env
OLLAMA_MODEL=llama3.2:1b
MAX_TOKENS=300
OLLAMA_OPTS="--num-gpu 1 --num-thread 16"
```

**Results:**
- Response time: <2 seconds (CPU), <500ms (GPU)
- Quality: Good for simple payloads, less detailed analysis
- Use case: Rapid testing, quick payload generation

#### Quality Response (Detailed Analysis)
```bash
# .env
OLLAMA_MODEL=dolphin-llama3
MAX_TOKENS=1024
OLLAMA_OPTS="--num-gpu 1 --num-thread 8"
```

**Results:**
- Response time: 30-60 seconds (CPU), 2-4 seconds (GPU)
- Quality: Excellent for complex analysis, full PoC code
- Use case: Detailed vulnerability analysis, CVSS scoring

#### Balanced (Default)
```bash
OLLAMA_MODEL=llama3.2
MAX_TOKENS=512
```

**Results:**
- Response time: 15-30 seconds (CPU), 1-2 seconds (GPU)
- Quality: Good balance
- Use case: General use

---

### Context Window Tuning

Larger context = remembers more conversation history, but slower.

```bash
# .env
MAX_HISTORY=5   # Only keep last 5 messages (fast)
# vs
MAX_HISTORY=50  # Keep last 50 messages (slow but better context)
```

**Impact:**
- `MAX_HISTORY=5`: +30% speed, -20% context quality
- `MAX_HISTORY=20`: Default (balanced)
- `MAX_HISTORY=50`: -40% speed, +40% context quality

---

### Token Count Tuning

```bash
# Fast responses (short payloads/explanations)
MAX_TOKENS=300

# Standard
MAX_TOKENS=512

# Detailed responses (full PoC, CVSS analysis)
MAX_TOKENS=1024

# Maximum (for very detailed analysis)
MAX_TOKENS=2048
```

---

## Memory Optimization

### Check Memory Usage

```bash
# Monitor Ollama process
watch -n 1 'ps aux | grep ollama | grep -v grep'

# Or with top
top -p $(pgrep -f ollama)
```

### Reduce Memory Footprint

1. **Limit model layers on GPU:**
```bash
export OLLAMA_NUM_GPU=0  # Force CPU-only (much slower but minimal VRAM)
export OLLAMA_NUM_GPU=1  # Use 1 GPU layer
```

2. **Unload model after use:**
```bash
# Set keep-alive to 0 (unload immediately after request)
export OLLAMA_OPTS="--keep-alive 0"

# Or auto-unload after 1 minute of inactivity
export OLLAMA_OPTS="--keep-alive 1m"
```

3. **Reduce batch size:**
```bash
export OLLAMA_OPTS="--batch-size 256"  # Default is 512
```

---

## Model Quantization

Smaller quantization = faster but lower quality.

| Quantization | Size | Speed (CPU) | Speed (GPU) | Quality |
|---|---|---|---|---|
| q2_K | 2.7 GB | 5-8s | <500ms | Poor |
| q3_K | 3.3 GB | 8-12s | <500ms | Fair |
| q4_0 | 4.7 GB | 20-30s | 1-2s | Good |
| q4_K | 5.2 GB | 25-35s | 1-2s | Good |
| q5_0 | 6.0 GB | 35-50s | 2-3s | Very Good |
| q5_K | 6.5 GB | 40-60s | 2-3s | Very Good |
| q6_K | 7.4 GB | 50-70s | 3-4s | Excellent |
| fp16 | 13 GB | 90-120s | 5-8s | Perfect |

### Use Cases by Quantization

- **q2_K/q3_K**: Ultra-fast recon, barely enough for pentesting
- **q4_0/q4_K**: Default (dolphin-llama3), recommended
- **q5_0+**: High-quality analysis when speed isn't critical
- **fp16**: Research, when quality is paramount

---

## Multi-GPU Setup

### Run Ollama on Specific GPUs

```bash
# Use GPU 0 only
export CUDA_VISIBLE_DEVICES=0
ollama serve

# Use both GPU 0 and 1
export CUDA_VISIBLE_DEVICES=0,1
export OLLAMA_NUM_GPU=2
ollama serve

# Distribute models across GPUs
OLLAMA_NUM_GPU=1 ollama serve  # Each model on 1 GPU
```

### Monitor GPU Usage

```bash
nvidia-smi
# or watch live
watch -n 1 nvidia-smi

# Per-process breakdown
nvidia-smi pmon
```

---

## X-ONE Specific Tuning

### For Bug Bounty (Speed Priority)

```bash
# .env
OLLAMA_MODEL=llama3.2:1b
OLLAMA_URL=http://localhost:11434
PORT=7777
MAX_HISTORY=10
MAX_TOKENS=300
OLLAMA_OPTS="--num-gpu 1 --num-thread 16"
```

**Result:** Payloads every 2-5 seconds

### For Deep Analysis (Quality Priority)

```bash
OLLAMA_MODEL=dolphin-llama3
MAX_HISTORY=30
MAX_TOKENS=1024
OLLAMA_OPTS="--num-gpu 1 --num-thread 8"
```

**Result:** Detailed responses every 2-4 seconds (with GPU)

### Server Deployment (Balance)

```bash
OLLAMA_MODEL=llama3.2
MAX_HISTORY=20
MAX_TOKENS=512
OLLAMA_OPTS="--num-gpu 1 --num-thread 16 --keep-alive 5m"
```

---

## Troubleshooting

### Ollama Process Not Starting

```bash
# Check logs
journalctl -u ollama -n 50 --no-pager

# Try manual start
ollama serve

# Check if port 11434 is in use
lsof -i :11434
```

### GPU Not Used

```bash
# Verify CUDA/ROCm installation
nvidia-smi
rocm-smi

# Force CPU (debugging)
export OLLAMA_NUM_GPU=0
ollama serve

# Check Ollama process during inference
nvidia-smi  # While running chat
```

### Out of Memory

```bash
# Reduce GPU layers
export OLLAMA_NUM_GPU=0  # CPU only
export OLLAMA_OPTS="--keep-alive 0"  # Unload after use

# Use smaller model
ollama pull llama3.2:1b  # 1 GB vs 4.7 GB
```

### Slow Responses

```bash
# Check if model is loaded
ollama ps

# Measure response time
time curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"dolphin-llama3","prompt":"hi","stream":false}' \
  > /dev/null

# If slow, check:
# 1. CPU/GPU available
# 2. Model quantization
# 3. Context window size
```

---

## Monitoring Dashboard

Create `monitor.sh`:

```bash
#!/bin/bash
watch -c -n 1 '
echo "=== Ollama Status ==="
curl -s http://localhost:11434/api/tags | jq ".models[].name" | head -5
echo ""
echo "=== GPU Usage (NVIDIA) ==="
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | awk "{print \$1/\$2*100\"%\"}"
echo ""
echo "=== CPU Usage ==="
ps aux | grep "ollama serve" | grep -v grep | awk "{print \$3\"%\"}"
echo ""
echo "=== Memory Usage ==="
ps aux | grep "ollama serve" | grep -v grep | awk "{print \$6/1024\" MB\"}"
'
```

Run with:
```bash
chmod +x monitor.sh
./monitor.sh
```
