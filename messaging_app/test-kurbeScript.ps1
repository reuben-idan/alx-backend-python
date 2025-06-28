# Test script for kurbeScript functionality
# This script tests the key components that kurbeScript should verify

Write-Host "Testing kurbeScript functionality..." -ForegroundColor Green

# Test 1: Check if minikube is installed
Write-Host "`n[TEST 1] Checking if minikube is installed..." -ForegroundColor Yellow
try {
    $minikubeVersion = minikube version
    Write-Host "✓ Minikube is installed: $minikubeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Minikube is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install minikube: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
}

# Test 2: Check if kubectl is installed
Write-Host "`n[TEST 2] Checking if kubectl is installed..." -ForegroundColor Yellow
try {
    $kubectlVersion = kubectl version --client
    Write-Host "✓ kubectl is installed: $kubectlVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ kubectl is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install kubectl: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Yellow
}

# Test 3: Check if Docker is running
Write-Host "`n[TEST 3] Checking if Docker is running..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running or not installed" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop" -ForegroundColor Yellow
}

# Test 4: Check if minikube cluster is running
Write-Host "`n[TEST 4] Checking if minikube cluster is running..." -ForegroundColor Yellow
try {
    $minikubeStatus = minikube status
    if ($minikubeStatus -like "*Running*") {
        Write-Host "✓ Minikube cluster is running" -ForegroundColor Green
        
        # Test 5: Verify cluster with kubectl cluster-info
        Write-Host "`n[TEST 5] Verifying cluster with kubectl cluster-info..." -ForegroundColor Yellow
        try {
            $clusterInfo = kubectl cluster-info
            Write-Host "✓ Cluster is accessible" -ForegroundColor Green
            Write-Host $clusterInfo -ForegroundColor Cyan
        } catch {
            Write-Host "✗ Cannot access cluster" -ForegroundColor Red
        }
        
        # Test 6: Retrieve available pods
        Write-Host "`n[TEST 6] Retrieving available pods..." -ForegroundColor Yellow
        try {
            $pods = kubectl get pods --all-namespaces
            Write-Host "✓ Successfully retrieved pods" -ForegroundColor Green
            Write-Host $pods -ForegroundColor Cyan
        } catch {
            Write-Host "✗ Cannot retrieve pods" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Minikube cluster is not running" -ForegroundColor Red
        Write-Host "  Run: minikube start" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Cannot check minikube status" -ForegroundColor Red
}

Write-Host "`nTest completed!" -ForegroundColor Green
Write-Host "If all tests pass, your kurbeScript should work correctly." -ForegroundColor Cyan 