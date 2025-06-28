#!/bin/bash

# kurbeScript - Kubernetes Setup and Verification Script
# This script installs Kubernetes components and sets up a local cluster

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install kubectl
install_kubectl() {
    local os=$(detect_os)
    print_status "Installing kubectl for $os..."
    
    case $os in
        "linux")
            # Install kubectl on Linux
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
            chmod +x kubectl
            sudo mv kubectl /usr/local/bin/
            ;;
        "macos")
            # Install kubectl on macOS
            if command_exists brew; then
                brew install kubectl
            else
                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
                chmod +x kubectl
                sudo mv kubectl /usr/local/bin/
            fi
            ;;
        "windows")
            # Install kubectl on Windows
            print_warning "Please install kubectl manually on Windows:"
            print_warning "1. Download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/"
            print_warning "2. Add to PATH"
            return 1
            ;;
        *)
            print_error "Unsupported operating system: $os"
            return 1
            ;;
    esac
    
    print_status "kubectl installed successfully"
}

# Function to install Minikube
install_minikube() {
    local os=$(detect_os)
    print_status "Installing Minikube for $os..."
    
    case $os in
        "linux")
            # Install Minikube on Linux
            curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
            sudo install minikube-linux-amd64 /usr/local/bin/minikube
            rm minikube-linux-amd64
            ;;
        "macos")
            # Install Minikube on macOS
            if command_exists brew; then
                brew install minikube
            else
                curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
                sudo install minikube-darwin-amd64 /usr/local/bin/minikube
                rm minikube-darwin-amd64
            fi
            ;;
        "windows")
            # Install Minikube on Windows
            print_warning "Please install Minikube manually on Windows:"
            print_warning "1. Download from: https://minikube.sigs.k8s.io/docs/start/"
            print_warning "2. Run as administrator"
            return 1
            ;;
        *)
            print_error "Unsupported operating system: $os"
            return 1
            ;;
    esac
    
    print_status "Minikube installed successfully"
}

# Function to check and install Docker
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first:"
        print_error "https://docs.docker.com/get-docker/"
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        return 1
    fi
    
    print_status "Docker is installed and running"
}

# Function to start Kubernetes cluster
start_cluster() {
    print_status "Starting Kubernetes cluster with Minikube..."
    
    # Check if cluster is already running
    if minikube status | grep -q "Running"; then
        print_warning "Minikube cluster is already running"
        return 0
    fi
    
    # Start Minikube with specific configuration
    minikube start \
        --driver=docker \
        --cpus=2 \
        --memory=4096 \
        --disk-size=20g \
        --addons=ingress \
        --addons=metrics-server
    
    print_status "Kubernetes cluster started successfully"
}

# Function to verify cluster
verify_cluster() {
    print_status "Verifying Kubernetes cluster..."
    
    # Check cluster info
    print_status "Cluster information:"
    kubectl cluster-info
    
    # Check nodes
    print_status "Available nodes:"
    kubectl get nodes
    
    # Check if metrics server is running
    print_status "Checking metrics server:"
    kubectl get pods -n kube-system | grep metrics-server || print_warning "Metrics server not found"
    
    # Check default namespace
    print_status "Pods in default namespace:"
    kubectl get pods --all-namespaces
    
    print_status "Cluster verification completed"
}

# Function to show cluster status
show_cluster_status() {
    print_status "Current cluster status:"
    minikube status
    
    print_status "Cluster resources:"
    kubectl get nodes -o wide
    
    print_status "System pods:"
    kubectl get pods -n kube-system
}

# Function to enable addons
enable_addons() {
    print_status "Enabling useful addons..."
    
    # Enable ingress
    minikube addons enable ingress
    
    # Enable metrics server
    minikube addons enable metrics-server
    
    # Enable dashboard (optional)
    read -p "Do you want to enable Kubernetes dashboard? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        minikube addons enable dashboard
        print_status "Dashboard enabled. Access it with: minikube dashboard"
    fi
    
    print_status "Addons enabled successfully"
}

# Function to show useful commands
show_commands() {
    print_header "Useful Kubernetes Commands"
    echo "Cluster Management:"
    echo "  minikube start          - Start the cluster"
    echo "  minikube stop           - Stop the cluster"
    echo "  minikube delete         - Delete the cluster"
    echo "  minikube status         - Show cluster status"
    echo ""
    echo "Application Management:"
    echo "  kubectl get pods        - List all pods"
    echo "  kubectl get services    - List all services"
    echo "  kubectl get deployments - List all deployments"
    echo "  kubectl logs <pod>      - View pod logs"
    echo "  kubectl exec -it <pod> -- /bin/bash - Access pod shell"
    echo ""
    echo "Monitoring:"
    echo "  minikube dashboard      - Open Kubernetes dashboard"
    echo "  kubectl top nodes       - Show node resource usage"
    echo "  kubectl top pods        - Show pod resource usage"
    echo ""
    echo "Troubleshooting:"
    echo "  kubectl describe pod <pod>    - Describe pod details"
    echo "  kubectl get events            - Show cluster events"
    echo "  kubectl cluster-info          - Show cluster information"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Stop Minikube
    if minikube status | grep -q "Running"; then
        minikube stop
        print_status "Minikube stopped"
    fi
    
    # Delete Minikube cluster
    minikube delete
    print_status "Minikube cluster deleted"
}

# Main function
main() {
    print_header "Kubernetes Setup and Verification Script"
    
    # Check OS
    local os=$(detect_os)
    print_status "Detected OS: $os"
    
    # Check Docker
    check_docker || exit 1
    
    # Install kubectl if not present
    if ! command_exists kubectl; then
        install_kubectl || exit 1
    else
        print_status "kubectl is already installed"
    fi
    
    # Install Minikube if not present
    if ! command_exists minikube; then
        install_minikube || exit 1
    else
        print_status "Minikube is already installed"
    fi
    
    # Start cluster
    start_cluster || exit 1
    
    # Verify cluster
    verify_cluster || exit 1
    
    # Show cluster status
    show_cluster_status
    
    # Enable addons
    enable_addons
    
    # Show useful commands
    show_commands
    
    print_header "Setup Complete!"
    print_status "Your Kubernetes cluster is ready for use!"
    print_status "You can now deploy your Django messaging application."
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     - Start and verify Kubernetes cluster (default)"
    echo "  status    - Show cluster status"
    echo "  cleanup   - Stop and delete cluster"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0         - Start and setup cluster"
    echo "  $0 status  - Show current status"
    echo "  $0 cleanup - Clean up cluster"
}

# Parse command line arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "status")
        show_cluster_status
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 