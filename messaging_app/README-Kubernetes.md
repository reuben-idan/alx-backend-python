# Kubernetes Orchestration for Django Messaging App

## 🚀 Container Orchestration with Kubernetes

This setup demonstrates how to deploy your Django messaging application using Kubernetes (K8s) with Minikube for local development and testing.

## 📋 Prerequisites

### **Required Software:**

- **Docker Desktop** - For building and running containers
- **Minikube** - Local Kubernetes cluster
- **kubectl** - Kubernetes command-line tool

### **Installation Commands:**

**For Windows:**

```powershell
# Install Minikube
winget install minikube

# Install kubectl
winget install kubernetes-cli

# Start Minikube
minikube start
```

**For Linux:**

```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Start Minikube
minikube start
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│  Namespace: messaging-app                                   │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Django App    │    │   MySQL DB      │                │
│  │   (2 replicas)  │◄──►│   (1 replica)   │                │
│  │   Port: 8000    │    │   Port: 3306    │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ LoadBalancer    │    │ Persistent      │                │
│  │ Service         │    │ Volume          │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Horizontal Pod  │    │ ConfigMaps &    │                │
│  │ Autoscaler      │    │ Secrets         │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Kubernetes Configuration Files

### **Core Components:**

- **`namespace.yaml`** - Isolated namespace for the application
- **`configmap.yaml`** - Non-sensitive configuration data
- **`secret.yaml`** - Sensitive data (passwords, keys)
- **`mysql-pv.yaml`** - Persistent volume for database data
- **`mysql-deployment.yaml`** - MySQL database deployment
- **`mysql-init-configmap.yaml`** - Database initialization scripts
- **`django-deployment.yaml`** - Django application deployment
- **`hpa.yaml`** - Horizontal Pod Autoscaler

## 🚀 Quick Deployment

### **Option 1: Automated Deployment**

```powershell
cd messaging_app
.\k8s\deploy.ps1
```

### **Option 2: Manual Deployment**

```powershell
# 1. Start Minikube
minikube start

# 2. Build and load Docker image
docker build -t messaging-app:latest .
minikube image load messaging-app:latest

# 3. Deploy all components
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/mysql-init-configmap.yaml
kubectl apply -f k8s/mysql-pv.yaml
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/django-deployment.yaml
kubectl apply -f k8s/hpa.yaml

# 4. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=django -n messaging-app --timeout=300s
```

## 🔧 Kubernetes Best Practices Implemented

### **1. Declarative Configuration**

- All resources defined in YAML files
- Version controlled and reproducible deployments
- Clear separation of concerns

### **2. Namespace Isolation**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: messaging-app
  labels:
    environment: development
    app: django-messaging
```

### **3. ConfigMaps and Secrets**

- **ConfigMaps**: Store non-sensitive configuration
- **Secrets**: Store sensitive data (base64 encoded)
- Environment variables injected into containers

### **4. Health Checks**

```yaml
livenessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### **5. Resource Management**

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### **6. Persistent Storage**

- MySQL data persisted across pod restarts
- HostPath volume for local development
- Proper volume claims and mounts

### **7. Auto-scaling**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## 📊 Monitoring and Management

### **Check Deployment Status**

```powershell
# View all resources in namespace
kubectl get all -n messaging-app

# View pods
kubectl get pods -n messaging-app

# View services
kubectl get services -n messaging-app

# View persistent volumes
kubectl get pv,pvc -n messaging-app
```

### **View Logs**

```powershell
# Django application logs
kubectl logs -f deployment/django-deployment -n messaging-app

# MySQL database logs
kubectl logs -f deployment/mysql-deployment -n messaging-app

# Specific pod logs
kubectl logs <pod-name> -n messaging-app
```

### **Access Application**

```powershell
# Get Minikube IP
minikube ip

# Get service port
kubectl get service django-service -n messaging-app

# Access via browser
minikube service django-service -n messaging-app
```

### **Scale Application**

```powershell
# Scale Django deployment
kubectl scale deployment django-deployment --replicas=3 -n messaging-app

# Check HPA status
kubectl get hpa -n messaging-app
```

## 🔍 Troubleshooting

### **Common Issues and Solutions**

**1. Pods Not Starting**

```powershell
# Check pod status
kubectl describe pod <pod-name> -n messaging-app

# Check events
kubectl get events -n messaging-app --sort-by='.lastTimestamp'
```

**2. Database Connection Issues**

```powershell
# Check MySQL pod
kubectl exec -it <mysql-pod-name> -n messaging-app -- mysql -u messaging_user -p

# Check Django logs
kubectl logs deployment/django-deployment -n messaging-app
```

**3. Image Pull Issues**

```powershell
# Load image into Minikube
minikube image load messaging-app:latest

# Check available images
minikube image ls
```

**4. Service Not Accessible**

```powershell
# Check service endpoints
kubectl get endpoints django-service -n messaging-app

# Port forward for testing
kubectl port-forward service/django-service 8080:80 -n messaging-app
```

## 🛠️ Development Workflow

### **1. Local Development**

```powershell
# Start Minikube
minikube start

# Deploy application
.\k8s\deploy.ps1

# Access application
minikube service django-service -n messaging-app
```

### **2. Code Changes**

```powershell
# Rebuild image
docker build -t messaging-app:latest .

# Load into Minikube
minikube image load messaging-app:latest

# Restart deployment
kubectl rollout restart deployment/django-deployment -n messaging-app
```

### **3. Database Changes**

```powershell
# Run migrations
kubectl exec -it deployment/django-deployment -n messaging-app -- python manage.py migrate

# Create superuser
kubectl exec -it deployment/django-deployment -n messaging-app -- python manage.py createsuperuser
```

## 🧹 Cleanup

### **Remove All Resources**

```powershell
# Delete entire namespace
kubectl delete namespace messaging-app

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## 📈 Production Considerations

### **Security**

- Use proper secrets management
- Implement RBAC (Role-Based Access Control)
- Enable network policies
- Use TLS for all communications

### **Monitoring**

- Deploy Prometheus and Grafana
- Set up alerting rules
- Monitor resource usage
- Track application metrics

### **Scaling**

- Use proper resource limits
- Implement auto-scaling policies
- Consider using managed Kubernetes services
- Plan for multi-node clusters

### **Backup and Recovery**

- Regular database backups
- Volume snapshots
- Disaster recovery procedures
- Testing restore processes

## 🎯 Learning Outcomes

After completing this setup, you will understand:

- ✅ **Kubernetes core concepts** (Pods, Services, Deployments)
- ✅ **Container orchestration** principles and benefits
- ✅ **Declarative configuration** management
- ✅ **Health checks and monitoring**
- ✅ **Auto-scaling and resource management**
- ✅ **Persistent storage** in Kubernetes
- ✅ **Security best practices** (ConfigMaps, Secrets)
- ✅ **Troubleshooting** Kubernetes deployments

## 🔗 Useful Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Django on Kubernetes](https://kubernetes.io/docs/tutorials/stateful-application/django-on-kubernetes/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

---

**Happy Orchestrating! 🚀**
