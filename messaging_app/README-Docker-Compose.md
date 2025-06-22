# Docker Compose Multi-Container Setup

## 🐳 Django + MySQL Multi-Container Environment

This setup uses Docker Compose to run your Django messaging application with a MySQL database in separate containers.

## 📁 Files Created

- ✅ `docker-compose.yml` - Multi-container orchestration
- ✅ `env.example` - Environment variables template
- ✅ `.env` - Environment variables (created from template)
- ✅ `Dockerfile` - Updated for MySQL client
- ✅ `wait_for_db.py` - Django management command
- ✅ `setup-docker-compose.ps1` - Automated setup script
- ✅ `requirements.txt` - Updated with MySQL dependencies

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Django Web    │    │   MySQL DB      │
│   (Port 8000)   │◄──►│   (Port 3306)   │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Setup

```powershell
cd messaging_app
.\setup-docker-compose.ps1
```

### Option 2: Manual Setup

```powershell
# 1. Create .env file from template
copy env.example .env

# 2. Build and start services
docker-compose up --build

# 3. In a new terminal, run migrations
docker-compose exec web python manage.py migrate
```

### Option 3: Development Mode

```powershell
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Services Configuration

### Web Service (Django)

- **Image**: Built from local Dockerfile
- **Port**: 8000 (host) → 8000 (container)
- **Volumes**: Local code mounted for development
- **Dependencies**: Waits for database to be ready
- **Environment**: Database connection variables

### Database Service (MySQL)

- **Image**: mysql:8.0
- **Port**: 3306 (host) → 3306 (container)
- **Volumes**: Persistent data storage
- **Environment**: Database credentials

## 📋 Environment Variables

Create a `.env` file with these variables:

```env
# Database Configuration
MYSQL_DATABASE=messaging_db
MYSQL_USER=messaging_user
MYSQL_PASSWORD=messaging_password123
MYSQL_ROOT_PASSWORD=root_password123

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## 🛠️ Database Management

### Connect to MySQL

```powershell
# Connect to MySQL container
docker-compose exec db mysql -u messaging_user -p messaging_db

# Or connect from host
mysql -h localhost -P 3306 -u messaging_user -p messaging_db
```

### Run Django Management Commands

```powershell
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Database Backup/Restore

```powershell
# Backup database
docker-compose exec db mysqldump -u messaging_user -p messaging_db > backup.sql

# Restore database
docker-compose exec -T db mysql -u messaging_user -p messaging_db < backup.sql
```

## 🔍 Troubleshooting

### Common Issues

**1. Database Connection Failed**

```powershell
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Wait for database to be ready
docker-compose exec web python manage.py wait_for_db
```

**2. Port Already in Use**

```powershell
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :3306

# Stop conflicting services or change ports in docker-compose.yml
```

**3. Permission Issues**

```powershell
# Run as administrator
Start-Process powershell -Verb RunAs
cd messaging_app
docker-compose up --build
```

### Useful Commands

```powershell
# View running containers
docker-compose ps

# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs web
docker-compose logs db

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

## 🧪 Testing the Setup

### 1. Check Web Service

- Open browser: `http://localhost:8000`
- Should see Django welcome page or your app

### 2. Check Database Connection

```powershell
# Test database connection
docker-compose exec web python manage.py dbshell
```

### 3. Create Test Data

```powershell
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 📊 Monitoring

### View Resource Usage

```powershell
# Container resource usage
docker stats

# Service status
docker-compose ps
```

### Health Checks

```powershell
# Check web service health
curl http://localhost:8000/health/

# Check database connectivity
docker-compose exec web python manage.py wait_for_db
```

## 🔄 Development Workflow

### 1. Start Development Environment

```powershell
docker-compose up -d
```

### 2. Make Code Changes

- Edit files in your local directory
- Changes are automatically reflected due to volume mounting

### 3. Run Tests

```powershell
docker-compose exec web python manage.py test
```

### 4. Apply Database Changes

```powershell
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 5. Stop Environment

```powershell
docker-compose down
```

## 🚀 Production Considerations

### Security

- Change default passwords in `.env`
- Use strong SECRET_KEY
- Set DEBUG=False
- Configure proper ALLOWED_HOSTS

### Performance

- Use production database (PostgreSQL recommended)
- Configure proper caching
- Use Gunicorn instead of Django dev server
- Set up reverse proxy (Nginx)

### Monitoring

- Add health check endpoints
- Configure logging
- Set up monitoring tools

---

**Happy Containerizing! 🐳**
