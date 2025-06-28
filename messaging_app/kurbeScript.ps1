# kurbeScript.ps1 - Kubernetes Setup and Verification Script for Windows
# This script installs Kubernetes components and sets up a local cluster

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "status", "cleanup", "help")]
    [string]$Action = "start"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Header {
    param([string]$Message)
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to install kubectl
function Install-Kubectl {
    Write-Status "Installing kubectl..."
    
    try {
        # Download kubectl
        $kubectlUrl = "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"
        $kubectlPath = "$env:USERPROFILE\.kube\kubectl.exe"
        
        # Create directory if it doesn't exist
        if (!(Test-Path "$env:USERPROFILE\.kube")) {
            New-Item -ItemType Directory -Path "$env:USERPROFILE\.kube" -Force | Out-Null
        }
        
        # Download kubectl
        Invoke-WebRequest -Uri $kubectlUrl -OutFile $kubectlPath
        
        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$env:USERPROFILE\.kube*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$env:USERPROFILE\.kube", "User")
            $env:PATH = "$env:PATH;$env:USERPROFILE\.kube"
        }
        
        Write-Status "kubectl installed successfully"
    } catch {
        Write-Error "Failed to install kubectl: $($_.Exception.Message)"
        Write-Warning "Please install kubectl manually from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/"
        return $false
    }
}

# Function to install Minikube
function Install-Minikube {
    Write-Status "Installing Minikube..."
    
    try {
        # Download Minikube
        $minikubeUrl = "https://github.com/kubernetes/minikube/releases/latest/download/minikube-windows-amd64.exe"
        $minikubePath = "$env:USERPROFILE\.minikube\minikube.exe"
        
        # Create directory if it doesn't exist
        if (!(Test-Path "$env:USERPROFILE\.minikube")) {
            New-Item -ItemType Directory -Path "$env:USERPROFILE\.minikube" -Force | Out-Null
        }
        
        # Download Minikube
        Invoke-WebRequest -Uri $minikubeUrl -OutFile $minikubePath
        
        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$env:USERPROFILE\.minikube*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$env:USERPROFILE\.minikube", "User")
            $env:PATH = "$env:PATH;$env:USERPROFILE\.minikube"
        }
        
        Write-Status "Minikube installed successfully"
    } catch {
        Write-Error "Failed to install Minikube: $($_.Exception.Message)"
        Write-Warning "Please install Minikube manually from: https://minikube.sigs.k8s.io/docs/start/"
        return $false
    }
}

# Function to check Docker
function Test-Docker {
    Write-Status "Checking Docker installation..."
    
    if (!(Test-Command "docker")) {
        Write-Error "Docker is not installed. Please install Docker Desktop first:"
        Write-Error "https://docs.docker.com/desktop/install/windows-install/"
        return $false
    }
    
    # Check if Docker daemon is running
    try {
        docker info | Out-Null
        Write-Status "Docker is installed and running"
        return $true
    } catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop first."
        return $false
    }
}

# Function to start Kubernetes cluster
function Start-Cluster {
    Write-Status "Starting Kubernetes cluster with Minikube..."
    
    try {
        # Check if cluster is already running
        $status = minikube status
        if ($status -like "*Running*") {
            Write-Warning "Minikube cluster is already running"
            return $true
        }
        
        # Start Minikube
        minikube start --driver=docker --cpus=2 --memory=4096 --disk-size=20g
        
        Write-Status "Kubernetes cluster started successfully"
        return $true
    } catch {
        Write-Error "Failed to start cluster: $($_.Exception.Message)"
        return $false
    }
}

# Function to verify cluster
function Test-Cluster {
    Write-Status "Verifying Kubernetes cluster..."
    
    try {
        # Check cluster info
        Write-Status "Cluster information:"
        kubectl cluster-info
        
        # Check nodes
        Write-Status "Available nodes:"
        kubectl get nodes
        
        # Check pods in all namespaces
        Write-Status "Pods in all namespaces:"
        kubectl get pods --all-namespaces
        
        Write-Status "Cluster verification completed"
        return $true
    } catch {
        Write-Error "Failed to verify cluster: $($_.Exception.Message)"
        return $false
    }
}

# Function to show cluster status
function Show-ClusterStatus {
    Write-Status "Current cluster status:"
    try {
        minikube status
    } catch {
        Write-Error "Failed to get cluster status"
    }
    
    Write-Status "Cluster resources:"
    try {
        kubectl get nodes -o wide
    } catch {
        Write-Error "Failed to get node information"
    }
    
    Write-Status "System pods:"
    try {
        kubectl get pods -n kube-system
    } catch {
        Write-Error "Failed to get system pods"
    }
}

# Function to enable addons
function Enable-Addons {
    Write-Status "Enabling useful addons..."
    
    try {
        # Enable ingress
        minikube addons enable ingress
        
        # Enable metrics server
        minikube addons enable metrics-server
        
        # Enable dashboard
        $response = Read-Host "Do you want to enable Kubernetes dashboard? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            minikube addons enable dashboard
            Write-Status "Dashboard enabled. Access it with: minikube dashboard"
        }
        
        Write-Status "Addons enabled successfully"
    } catch {
        Write-Error "Failed to enable addons: $($_.Exception.Message)"
    }
}

# Function to show useful commands
function Show-Commands {
    Write-Header "Useful Kubernetes Commands"
    Write-Host "Cluster Management:" -ForegroundColor Yellow
    Write-Host "  minikube start          - Start the cluster"
    Write-Host "  minikube stop           - Stop the cluster"
    Write-Host "  minikube delete         - Delete the cluster"
    Write-Host "  minikube status         - Show cluster status"
    Write-Host ""
    Write-Host "Application Management:" -ForegroundColor Yellow
    Write-Host "  kubectl get pods        - List all pods"
    Write-Host "  kubectl get services    - List all services"
    Write-Host "  kubectl get deployments - List all deployments"
    Write-Host "  kubectl logs <pod>      - View pod logs"
    Write-Host "  kubectl exec -it <pod> -- /bin/bash - Access pod shell"
    Write-Host ""
    Write-Host "Monitoring:" -ForegroundColor Yellow
    Write-Host "  minikube dashboard      - Open Kubernetes dashboard"
    Write-Host "  kubectl top nodes       - Show node resource usage"
    Write-Host "  kubectl top pods        - Show pod resource usage"
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  kubectl describe pod <pod>    - Describe pod details"
    Write-Host "  kubectl get events            - Show cluster events"
    Write-Host "  kubectl cluster-info          - Show cluster information"
}

# Function to cleanup
function Remove-Cluster {
    Write-Status "Cleaning up..."
    
    try {
        # Stop Minikube
        $status = minikube status
        if ($status -like "*Running*") {
            minikube stop
            Write-Status "Minikube stopped"
        }
        
        # Delete Minikube cluster
        minikube delete
        Write-Status "Minikube cluster deleted"
    } catch {
        Write-Error "Failed to cleanup: $($_.Exception.Message)"
    }
}

# Function to show help
function Show-Help {
    Write-Host "Usage: .\kurbeScript.ps1 [OPTION]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  start     - Start and verify Kubernetes cluster (default)"
    Write-Host "  status    - Show cluster status"
    Write-Host "  cleanup   - Stop and delete cluster"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\kurbeScript.ps1         - Start and setup cluster"
    Write-Host "  .\kurbeScript.ps1 status  - Show current status"
    Write-Host "  .\kurbeScript.ps1 cleanup - Clean up cluster"
}

# Main function
function Start-KubernetesSetup {
    Write-Header "Kubernetes Setup and Verification Script for Windows"
    
    # Check Docker
    if (!(Test-Docker)) {
        exit 1
    }
    
    # Install kubectl if not present
    if (!(Test-Command "kubectl")) {
        if (!(Install-Kubectl)) {
            exit 1
        }
    } else {
        Write-Status "kubectl is already installed"
    }
    
    # Install Minikube if not present
    if (!(Test-Command "minikube")) {
        if (!(Install-Minikube)) {
            exit 1
        }
    } else {
        Write-Status "Minikube is already installed"
    }
    
    # Start cluster
    if (!(Start-Cluster)) {
        exit 1
    }
    
    # Verify cluster
    if (!(Test-Cluster)) {
        exit 1
    }
    
    # Show cluster status
    Show-ClusterStatus
    
    # Enable addons
    Enable-Addons
    
    # Show useful commands
    Show-Commands
    
    Write-Header "Setup Complete!"
    Write-Status "Your Kubernetes cluster is ready for use!"
    Write-Status "You can now deploy your Django messaging application."
}

# Parse command line arguments
switch ($Action) {
    "start" {
        Start-KubernetesSetup
    }
    "status" {
        Show-ClusterStatus
    }
    "cleanup" {
        Remove-Cluster
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown option: $Action"
        Show-Help
        exit 1
    }
} 