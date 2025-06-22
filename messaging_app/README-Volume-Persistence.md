# Docker Volume Persistence Setup

## 🗄️ Data Persistence with Docker Volumes

This setup ensures that your MySQL database data and other important files persist across container restarts, updates, and system reboots.

## 📁 Volume Configuration

### **Enhanced docker-compose.yml Features:**

1. **Database Data Persistence** - MySQL data survives container restarts
2. **Configuration Persistence** - MySQL settings are preserved
3. **Log Persistence** - Database logs are stored locally
4. **Backup Persistence** - Database backups are stored locally
5. **Static Files Persistence** - Django static files are preserved
6. **Media Files Persistence** - User uploads are preserved
7. **phpMyAdmin Configuration** - Database management interface settings

## 🏗️ Volume Architecture

```
Host Machine                    Docker Containers
┌─────────────────────────┐    ┌─────────────────┐
│ ./data/mysql/           │◄──►│ /var/lib/mysql  │
│ ./data/mysql-config/    │◄──►│ /etc/mysql/conf │
│ ./data/mysql-logs/      │◄──►│ /var/log/mysql  │
│ ./data/mysql-backup/    │◄──►│ /backup         │
│ ./data/staticfiles/     │◄──►│ /app/staticfiles│
│ ./data/media/           │◄──►│ /app/media      │
│ ./data/phpmyadmin/      │◄──►│ /var/www/html   │
└─────────────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### **Step 1: Setup Volume Directories**

```powershell
cd messaging_app
.\setup-volumes.ps1
```

### **Step 2: Start Services with Persistence**

```powershell
docker-compose up --build
```

### **Step 3: Verify Data Persistence**

```powershell
# Create some data in your app
# Stop containers
docker-compose down

# Start containers again
docker-compose up -d

# Your data should still be there!
```

## 📊 Volume Management

### **View Volume Information**

```powershell
.\volume-management.ps1 info
```

### **Create Database Backup**

```powershell
.\volume-management.ps1 backup
```

### **Restore Database from Backup**

```powershell
.\volume-management.ps1 restore
```

### **List All Volumes and Data**

```powershell
.\volume-management.ps1 list
```

### **Clean All Volumes (DESTRUCTIVE)**

```powershell
.\volume-management.ps1 clean
```

## 🔧 Volume Configuration Details

### **MySQL Database Volume**

```yaml
volumes:
  - mysql_data:/var/lib/mysql
```

- **Purpose**: Stores all database data, tables, and indexes
- **Persistence**: Survives container restarts and updates
- **Location**: `./data/mysql/` on host machine

### **MySQL Configuration Volume**

```yaml
volumes:
  - mysql_config:/etc/mysql/conf.d
```

- **Purpose**: Stores MySQL configuration files
- **Persistence**: Custom settings are preserved
- **Location**: `./data/mysql-config/` on host machine

### **MySQL Logs Volume**

```yaml
volumes:
  - mysql_logs:/var/log/mysql
```

- **Purpose**: Stores MySQL error and access logs
- **Persistence**: Logs are preserved for debugging
- **Location**: `./data/mysql-logs/` on host machine

### **Database Backup Volume**

```yaml
volumes:
  - mysql_backup:/backup
```

- **Purpose**: Stores database backup files
- **Persistence**: Backups are preserved locally
- **Location**: `./data/mysql-backup/` on host machine

### **Static Files Volume**

```yaml
volumes:
  - static_volume:/app/staticfiles
```

- **Purpose**: Stores Django static files (CSS, JS, images)
- **Persistence**: Static files are preserved
- **Location**: `./data/staticfiles/` on host machine

### **Media Files Volume**

```yaml
volumes:
  - media_volume:/app/media
```

- **Purpose**: Stores user-uploaded files
- **Persistence**: Uploads are preserved
- **Location**: `./data/media/` on host machine

## 🛠️ Manual Volume Operations

### **Backup Database Manually**

```powershell
# Create backup
docker-compose exec db mysqldump -u messaging_user -pmessaging_password123 messaging_db > backup.sql

# Restore backup
docker-compose exec -T db mysql -u messaging_user -pmessaging_password123 messaging_db < backup.sql
```

### **Access Volume Data Directly**

```powershell
# View database files
ls data/mysql/

# View logs
ls data/mysql-logs/

# View backups
ls data/mysql-backup/
```

### **Copy Data Between Volumes**

```powershell
# Copy database to host
docker cp <container_id>:/var/lib/mysql ./local-mysql-copy/

# Copy from host to container
docker cp ./local-mysql-copy/ <container_id>:/var/lib/mysql
```

## 🔍 Troubleshooting

### **Volume Not Persisting**

```powershell
# Check if volumes are properly mounted
docker-compose exec db ls -la /var/lib/mysql

# Check host directory permissions
ls -la data/mysql/
```

### **Permission Issues**

```powershell
# Fix directory permissions
chmod -R 755 data/
chown -R 1000:1000 data/mysql/
```

### **Volume Corruption**

```powershell
# Stop containers
docker-compose down

# Backup current data
cp -r data/mysql/ data/mysql-backup-$(date +%Y%m%d)/

# Clean and recreate
docker-compose down -v
.\setup-volumes.ps1
docker-compose up --build
```

### **Low Disk Space**

```powershell
# Check volume sizes
.\volume-management.ps1 list

# Clean old backups
ls data/mysql-backup/ | Sort-Object LastWriteTime | Select-Object -First 5
```

## 📈 Performance Considerations

### **Volume Performance Tips**

1. **Use SSD storage** for better I/O performance
2. **Monitor disk space** regularly
3. **Schedule regular backups**
4. **Use appropriate MySQL buffer sizes**

### **MySQL Optimization**

```yaml
command: >
  --default-authentication-plugin=mysql_native_password
  --character-set-server=utf8mb4
  --collation-server=utf8mb4_unicode_ci
  --innodb-buffer-pool-size=256M
  --max-connections=200
```

## 🔒 Security Considerations

### **Volume Security**

1. **Restrict access** to data directories
2. **Use strong passwords** in .env file
3. **Regular backups** to secure location
4. **Monitor logs** for suspicious activity

### **Backup Security**

```powershell
# Encrypt backups
gpg -e backup.sql

# Store backups offsite
rsync -av data/mysql-backup/ /mnt/backup-drive/
```

## 📋 Best Practices

### **Regular Maintenance**

1. **Daily**: Check container status
2. **Weekly**: Create database backups
3. **Monthly**: Review and clean old logs
4. **Quarterly**: Test restore procedures

### **Monitoring**

```powershell
# Check volume health
.\volume-management.ps1 info

# Monitor disk usage
df -h data/

# Check container logs
docker-compose logs db
```

## 🎯 Expected Results

After implementing volume persistence:

- ✅ **Database data survives** container restarts
- ✅ **User uploads are preserved** across deployments
- ✅ **Static files are cached** and served efficiently
- ✅ **Logs are accessible** for debugging
- ✅ **Backups are automated** and secure
- ✅ **Configuration changes** are preserved

---

**Your data is now safe and persistent! 🗄️**
