# Docker Setup Guide for Django Messaging App

## Prerequisites

- Docker Desktop installed and running
- Python virtual environment with dependencies

## Files Created

✅ `requirements.txt` - Contains all Python dependencies
✅ `Dockerfile` - Container configuration
✅ `docker-compose.yml` - Optional orchestration

## Step-by-Step Implementation

### 1. Verify Docker is Running

```powershell
docker --version
docker info
```

### 2. Build the Docker Image

```powershell
cd messaging_app
docker build -t messaging-app .
```

### 3. Run the Container

```powershell
docker run -p 8000:8000 messaging-app
```

### 4. Alternative: Run in Background

```powershell
docker run -d -p 8000:8000 --name messaging-container messaging-app
```

### 5. Check Container Status

```powershell
docker ps
docker logs messaging-container
```

### 6. Stop Container

```powershell
docker stop messaging-container
docker rm messaging-container
```

## Troubleshooting

### If Docker commands hang:

1. Start Docker Desktop
2. Wait for it to fully load
3. Restart PowerShell/Command Prompt
4. Try commands again

### If build fails:

1. Check internet connection
2. Ensure requirements.txt is in the same directory as Dockerfile
3. Verify Docker Desktop has enough resources allocated

## Expected Output

After successful build and run:

- Django development server should start
- App accessible at http://localhost:8000
- Container logs showing Django startup messages

## Files Structure

```
messaging_app/
├── Dockerfile
├── requirements.txt
├── manage.py
├── messaging_app/
├── chats/
└── docker-setup.md
```
