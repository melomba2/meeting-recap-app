# Meeting Recap API - Usage Examples

## Server Information

- **Base URL**: `http://127.0.0.1:8765`
- **API Key Header**: `X-API-Key: your_api_key`
- **Interactive Docs**: http://127.0.0.1:8765/docs
- **OpenAPI Spec**: http://127.0.0.1:8765/openapi.json

## Starting the Server

```bash
python3 src-python/api_server.py
```

The server will start on port 8765 and bind to localhost only (127.0.0.1) for security.

## Authentication

All endpoints (except `/docs` and `/openapi.json`) require API key authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key" http://127.0.0.1:8765/
```

**Note**: Change `your_api_key` to a secure key in production by editing `api_server.py` line 22.

## API Endpoints

### 1. Root Endpoint (Health Check)

**Request:**
```bash
curl -H "X-API-Key: your_api_key" http://127.0.0.1:8765/
```

**Response:**
```json
{
  "message": "Meeting Recap API server is running!"
}
```

---

### 2. List All Jobs

Get a list of all processing jobs (queued, processing, completed, or failed).

**Request:**
```bash
curl -H "X-API-Key: your_api_key" http://127.0.0.1:8765/api/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "type": "transcribe",
      "created_at": "2025-10-28T20:30:00.000000"
    }
  ]
}
```

---

### 3. Transcribe Audio/Video File

Start a transcription job using Whisper.

**Request:**
```bash
curl -X POST http://127.0.0.1:8765/api/transcribe \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/your/recording.mp4",
    "model": "medium",
    "output_dir": "/path/to/output"
  }'
```

**Parameters:**
- `file_path` (required): Absolute path to audio/video file
- `model` (optional): Whisper model size - `tiny`, `base`, `small`, `medium` (default), `large`
- `output_dir` (optional): Output directory (defaults to same directory as input file)

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Transcription job queued"
}
```

**Example with Actual File:**
```bash
# Create a test directory and use an existing audio file
curl -X POST http://127.0.0.1:8765/api/transcribe \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/Users/michaellombard/Downloads/meeting.mp4",
    "model": "small"
  }'
```

---

### 4. Analyze Transcript

Analyze a transcript file using Ollama/Gemma3n.

**Request:**
```bash
curl -X POST http://127.0.0.1:8765/api/analyze \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_path": "/path/to/transcript.txt",
    "model": "gemma3n:latest",
    "ollama_url": "http://192.168.68.10:11434",
    "output_dir": "/path/to/output"
  }'
```

**Parameters:**
- `transcript_path` (required): Path to transcript text file
- `model` (optional): Ollama model name (default: `gemma3n:latest`)
- `ollama_url` (optional): Ollama server URL (default: `http://192.168.68.10:11434`)
- `output_dir` (optional): Output directory

**Response:**
```json
{
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "queued",
  "message": "Analysis job queued"
}
```

---

### 5. Generate Recap

Generate a D&D-style narrative recap from an analysis file.

**Request:**
```bash
curl -X POST http://127.0.0.1:8765/api/recap \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_path": "/path/to/analysis.txt",
    "style": "epic",
    "ollama_url": "http://192.168.68.10:11434",
    "output_dir": "/path/to/output"
  }'
```

**Parameters:**
- `analysis_path` (required): Path to analysis text file
- `style` (optional): Recap style - `epic` (default), `casual`, `dramatic`, `narrative`
- `ollama_url` (optional): Ollama server URL (default: `http://192.168.68.10:11434`)
- `output_dir` (optional): Output directory

**Response:**
```json
{
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "queued",
  "message": "Recap generation job queued"
}
```

---

### 6. Check Job Status

Get the status and results of a specific job.

**Request:**
```bash
curl -H "X-API-Key: your_api_key" \
  http://127.0.0.1:8765/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response (In Progress):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "stage": "transcription",
  "error": null,
  "result": null
}
```

**Response (Completed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "stage": "transcription",
  "error": null,
  "result": {
    "transcript_path": "/path/to/transcript.txt",
    "duration": "8m 34s",
    "model": "medium"
  }
}
```

**Response (Failed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 25,
  "stage": "transcription",
  "error": "File not found: /path/to/file.mp4",
  "result": null
}
```

---

## Complete Workflow Example

Here's a complete example of processing a recording from start to finish:

```bash
# 1. Start a transcription job
TRANSCRIBE_RESPONSE=$(curl -s -X POST http://127.0.0.1:8765/api/transcribe \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/Users/michaellombard/Downloads/dnd-session-42.mp4",
    "model": "medium"
  }')

# Extract job ID
TRANSCRIBE_JOB_ID=$(echo $TRANSCRIBE_RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
echo "Transcription job started: $TRANSCRIBE_JOB_ID"

# 2. Poll for completion
while true; do
  STATUS=$(curl -s -H "X-API-Key: your_api_key" \
    http://127.0.0.1:8765/api/status/$TRANSCRIBE_JOB_ID | \
    grep -o '"status":"[^"]*"' | cut -d'"' -f4)

  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Transcription failed!"
    exit 1
  fi

  sleep 5
done

# 3. Get the transcript path from results
TRANSCRIPT_PATH=$(curl -s -H "X-API-Key: your_api_key" \
  http://127.0.0.1:8765/api/status/$TRANSCRIBE_JOB_ID | \
  grep -o '"transcript_path":"[^"]*"' | cut -d'"' -f4)

echo "Transcript saved to: $TRANSCRIPT_PATH"

# 4. Start analysis job
ANALYZE_RESPONSE=$(curl -s -X POST http://127.0.0.1:8765/api/analyze \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d "{
    \"transcript_path\": \"$TRANSCRIPT_PATH\",
    \"model\": \"gemma3n:latest\"
  }")

ANALYZE_JOB_ID=$(echo $ANALYZE_RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
echo "Analysis job started: $ANALYZE_JOB_ID"

# 5. Wait for analysis to complete (similar polling as above)
# ... (omitted for brevity)

# 6. Start recap generation job
# ... (similar pattern)
```

---

## Error Responses

### 401 Unauthorized (Missing/Invalid API Key)

```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found (Invalid Job ID)

```json
{
  "detail": "Job not found"
}
```

### 404 Not Found (File Not Found)

```json
{
  "detail": "File not found"
}
```

---

## Python Client Example

```python
import requests
import time

API_BASE = "http://127.0.0.1:8765"
API_KEY = "your_api_key"
HEADERS = {"X-API-Key": API_KEY}

# Start transcription
response = requests.post(
    f"{API_BASE}/api/transcribe",
    headers=HEADERS,
    json={
        "file_path": "/path/to/recording.mp4",
        "model": "medium"
    }
)
job_id = response.json()["job_id"]
print(f"Job started: {job_id}")

# Poll for completion
while True:
    status_response = requests.get(
        f"{API_BASE}/api/status/{job_id}",
        headers=HEADERS
    )
    data = status_response.json()

    print(f"Status: {data['status']} ({data.get('progress', 0)}%)")

    if data["status"] == "completed":
        print(f"Results: {data['result']}")
        break
    elif data["status"] == "failed":
        print(f"Error: {data['error']}")
        break

    time.sleep(5)
```

---

## Security Notes

1. **Change the default API key** in `api_server.py` before deploying
2. **Only binds to localhost** (127.0.0.1) - not accessible from network
3. **Use HTTPS** if exposing to network (requires reverse proxy like nginx)
4. **Implement rate limiting** for production use
5. **Validate file paths** to prevent directory traversal attacks
6. **Store API keys securely** (environment variables, not in code)

---

## Troubleshooting

**Server won't start - Port already in use:**
```bash
lsof -ti:8765 | xargs kill -9
```

**Import errors:**
```bash
pip3 install fastapi uvicorn torch whisper requests
```

**CUDA/GPU not detected:**
- Verify CUDA drivers: `nvidia-smi`
- Check PyTorch installation: `python3 -c "import torch; print(torch.cuda.is_available())"`

**Ollama connection refused:**
- Start Ollama: `ollama serve`
- Verify: `curl http://192.168.68.10:11434/api/tags`
- Pull model: `ollama pull gemma3n:latest`
