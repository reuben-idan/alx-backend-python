Write-Host "========================================" -ForegroundColor Green
Write-Host "Kubernetes Deployment for Django Messaging App" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Checking Minikube status..." -ForegroundColor Yellow
try {
    $minikubeStatus = minikube status
    Write-Host "✓ Minikube status:" -ForegroundColor Green
    Write-Host $minikubeStatus -ForegroundColor White
} catch {
    Write-Host "✗ Minikube not found or not running" -ForegroundColor Red
    Write-Host "Please install and start Minikube first:" -ForegroundColor Yellow
    Write-Host "  minikube start" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "2. Building Docker image..." -ForegroundColor Yellow
try {
    # Build the Docker image
    docker build -t messaging-app:latest .
    Write-Host "✓ Docker image built successfully" -ForegroundColor Green
    
    # Load image into Minikube
    minikube image load messaging-app:latest
    Write-Host "✓ Image loaded into Minikube" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to build or load Docker image" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. Creating namespace..." -ForegroundColor Yellow
try {
    kubectl apply -f k8s/namespace.yaml
    Write-Host "✓ Namespace created" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create namespace" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "4. Creating ConfigMaps and Secrets..." -ForegroundColor Yellow
try {
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secret.yaml
    kubectl apply -f k8s/mysql-init-configmap.yaml
    Write-Host "✓ ConfigMaps and Secrets created" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create ConfigMaps and Secrets" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "5. Creating Persistent Volumes..." -ForegroundColor Yellow
try {
    kubectl apply -f k8s/mysql-pv.yaml
    Write-Host "✓ Persistent Volumes created" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create Persistent Volumes" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "6. Deploying MySQL..." -ForegroundColor Yellow
try {
    kubectl apply -f k8s/mysql-deployment.yaml
    Write-Host "✓ MySQL deployment created" -ForegroundColor Green
    
    # Wait for MySQL to be ready
    Write-Host "Waiting for MySQL to be ready..." -ForegroundColor Cyan
    kubectl wait --for=condition=ready pod -l app=mysql -n messaging-app --timeout=300s
    Write-Host "✓ MySQL is ready" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to deploy MySQL" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "7. Deploying Django application..." -ForegroundColor Yellow
try {
    kubectl apply -f k8s/django-deployment.yaml
    Write-Host "✓ Django deployment created" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to deploy Django" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "8. Creating Horizontal Pod Autoscaler..." -ForegroundColor Yellow
try {
    kubectl apply -f k8s/hpa.yaml
    Write-Host "✓ HPA created" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create HPA" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "9. Waiting for all pods to be ready..." -ForegroundColor Yellow
try {
    kubectl wait --for=condition=ready pod -l app=django -n messaging-app --timeout=300s
    Write-Host "✓ All pods are ready" -ForegroundColor Green
} catch {
    Write-Host "✗ Some pods are not ready" -ForegroundColor Red
}

Write-Host ""
Write-Host "10. Getting service information..." -ForegroundColor Yellow
try {
    $serviceInfo = kubectl get service django-service -n messaging-app
    Write-Host "✓ Service information:" -ForegroundColor Green
    Write-Host $serviceInfo -ForegroundColor White
    
    # Get Minikube IP
    $minikubeIP = minikube ip
    Write-Host "Minikube IP: $minikubeIP" -ForegroundColor Cyan
    
    # Get service port
    $servicePort = kubectl get service django-service -n messaging-app -o jsonpath='{.spec.ports[0].nodePort}'
    Write-Host "Service Port: $servicePort" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
    Write-Host "Your Django app should be accessible at:" -ForegroundColor Cyan
    Write-Host "http://$minikubeIP`:$servicePort" -ForegroundColor White
    
} catch {
    Write-Host "✗ Failed to get service information" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  kubectl get pods -n messaging-app" -ForegroundColor White
Write-Host "  kubectl get services -n messaging-app" -ForegroundColor White
Write-Host "  kubectl logs -f deployment/django-deployment -n messaging-app" -ForegroundColor White
Write-Host "  kubectl logs -f deployment/mysql-deployment -n messaging-app" -ForegroundColor White
Write-Host "  kubectl delete namespace messaging-app" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green 