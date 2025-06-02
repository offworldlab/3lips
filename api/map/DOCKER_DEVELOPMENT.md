# Docker Development Setup with Hot-Reloading

## Overview

Enable hot-reloading for 3lips development so you don't need to rebuild the Docker container every time you make changes.

## Option 1: Volume Mounts (Recommended)

Mount your source code as volumes in the Docker container so changes are reflected immediately.

### Docker Compose Method

Create or modify `docker-compose.dev.yml`:

```yaml
version: '3.8'
services:
  threelips:
    build: .
    ports:
      - "8080:8080"
    volumes:
      # Mount the entire source code for hot reloading
      - ./3lips/api:/app/3lips/api:ro
      - ./3lips/event:/app/3lips/event:ro
      - ./3lips/common:/app/3lips/common:ro
      # Mount specific files you're working on
      - ./3lips/api/map/event/tracks.js:/app/3lips/api/map/event/tracks.js:ro
      - ./3lips/api/map/index.html:/app/3lips/api/map/index.html:ro
      - ./3lips/api/map/main.js:/app/3lips/api/map/main.js:ro
    environment:
      - TRACKER_VERBOSE=true
      - NODE_ENV=development
    command: ["python3", "-u", "/app/3lips/event/event.py"]  # -u for unbuffered output
```

Run with:
```bash
docker-compose -f docker-compose.dev.yml up
```

### Docker Run Method

```bash
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/3lips/api:/app/3lips/api:ro \
  -v $(pwd)/3lips/event:/app/3lips/event:ro \
  -v $(pwd)/3lips/common:/app/3lips/common:ro \
  -e TRACKER_VERBOSE=true \
  your-threelips-image
```

## Option 2: Development Dockerfile

Create `Dockerfile.dev`:

```dockerfile
FROM your-base-image

# Install development dependencies
RUN pip install watchdog  # For Python file watching
RUN npm install -g nodemon  # For JavaScript file watching (if needed)

# Copy source with development settings
COPY . /app
WORKDIR /app

# Use a development command that watches for changes
CMD ["python3", "-u", "-m", "watchdog", "tricks.auto_restart", "--patterns='*.py'", "--restart-cmd='python3 /app/3lips/event/event.py'"]
```

## Option 3: File Watching with Docker

### Python File Watching

Install `watchdog` in your container and use:

```python
# dev_runner.py
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, process_args):
        self.process_args = process_args
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print("Restarting application...")
        self.process = subprocess.Popen(self.process_args)

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            self.restart()

if __name__ == "__main__":
    handler = RestartHandler(['python3', '/app/3lips/event/event.py'])
    observer = Observer()
    observer.schedule(handler, '/app/3lips', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

### Static File Serving

For frontend files (HTML, JS, CSS), make sure your web server serves files directly from the mounted volume without caching:

```python
# In your Flask/web server setup
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching
```

## Option 4: Remote Development

Use VS Code Remote Containers or similar:

1. Install "Remote - Containers" extension in VS Code
2. Create `.devcontainer/devcontainer.json`:

```json
{
    "name": "3lips Development",
    "dockerComposeFile": "../docker-compose.dev.yml",
    "service": "threelips",
    "workspaceFolder": "/app",
    "settings": {
        "python.defaultInterpreterPath": "/usr/bin/python3"
    },
    "extensions": [
        "ms-python.python",
        "ms-vscode.vscode-json"
    ],
    "forwardPorts": [8080],
    "postCreateCommand": "pip install watchdog"
}
```

## Current Implementation Tips

### For JavaScript Changes (tracks.js, main.js, etc.)
- These are served as static files, so volume mounts will work immediately
- Browser refresh will pick up changes
- No server restart needed

### For Python Changes (event.py, Track.py, etc.)
- Requires process restart or file watching
- Use volume mounts + process restart script
- Or use watchdog for automatic restart

### For Configuration Changes
- Environment variables may require container restart
- Config files can use volume mounts

## Debug Your Setup

Test if hot-reloading is working:

1. **JavaScript**: Add a `console.log("TEST")` to tracks.js and refresh browser
2. **Python**: Add a `print("TEST")` to event.py and check if it appears in logs
3. **HTML**: Modify the legend text in index.html and refresh

## Recommended Development Workflow

1. Use Docker Compose with volume mounts for active development
2. Set `TRACKER_VERBOSE=true` for detailed logging
3. Use browser dev tools for frontend debugging
4. Use `docker logs -f container_name` for backend debugging
5. Keep a terminal open with `docker-compose logs -f` for real-time logs

## Performance Considerations

- Volume mounts can be slower on macOS/Windows (use Docker Desktop's performance settings)
- Consider using named volumes for node_modules if you have Node.js dependencies
- Use `.dockerignore` to exclude unnecessary files from build context 