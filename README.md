# Kubernetes Basics

> **What you'll create:** Deploy a containerized application to Kubernetes with proper deployments, services, config management, and health checks.

---

## Quick Start

```bash
# 1. Fork and clone this repo

# 2. Install tools (see Step 0)

# 3. Complete the K8s manifests in k8s/ folder

# 4. Push and check your score
git push origin main
# → Check GitHub Actions tab!
```

---

## What is This Challenge?

You have a Docker container. Now you need to run it in **production** - that means:
- Multiple copies for reliability
- Automatic restart if it crashes
- Load balancing between copies
- Configuration management
- Secure secrets handling

**Kubernetes** does all of this. Let's learn how!

---

## Do I Need Prior Knowledge?

**You need:**
- ✅ Completed Challenge 1.2 (Dockerize) OR understand Docker basics
- ✅ Basic YAML syntax

**You'll learn:**
- What Kubernetes is and why it matters
- Pods, Deployments, Services, ConfigMaps, Secrets
- How to write Kubernetes manifests
- Health checks (liveness/readiness probes)

---

## What You'll Build

| File | What You Create | Points |
|------|-----------------|--------|
| `k8s/deployment.yaml` | Deployment with 2+ replicas | 25 |
| `k8s/service.yaml` | Service to expose the app | 20 |
| `k8s/configmap.yaml` | Configuration management | 15 |
| `k8s/secret.yaml` | Secure secrets handling | 15 |
| Health checks | Liveness & readiness probes | 15 |
| Resource limits | CPU/memory limits | 10 |

---

## Step 0: Install Kubernetes Tools

> ⏱️ **Time:** 15-20 minutes (one-time setup)

### Prerequisites: Docker Required

**Kind runs Kubernetes clusters inside Docker containers.** You must have Docker installed and running before proceeding.

If you haven't installed Docker yet:
- Complete **Challenge 1.2 (Dockerize Python App)** first - it includes Docker installation instructions
- Or install Docker Desktop from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

**Verify Docker is running:**
```bash
docker --version
# Should show: Docker version 24.x or higher

docker ps
# Should work without errors (may show empty list)
```

### What is Kubernetes?

**Kubernetes (K8s)** is a container orchestration platform. It:
- Runs containers across multiple machines
- Automatically restarts crashed containers
- Scales up/down based on load
- Manages networking between containers
- Handles configuration and secrets

```
Without Kubernetes:
"I have 10 servers, how do I deploy to all of them?"
"Container crashed, who restarts it?"
"How do I update without downtime?"

With Kubernetes:
"Deploy this to the cluster" → K8s figures out the rest
"Container crashed" → K8s restarts automatically
"Update deployment" → K8s does rolling update
```

### Install kubectl

**kubectl** is the command-line tool for Kubernetes.

<details>
<summary>🪟 Windows</summary>

**Option 1: Chocolatey**
```powershell
choco install kubernetes-cli
```

**Option 2: Direct download**
```powershell
curl -LO "https://dl.k8s.io/release/v1.29.0/bin/windows/amd64/kubectl.exe"
# Move to a folder in your PATH
```

**Verify:**
```bash
kubectl version --client
```

</details>

<details>
<summary>🍎 Mac</summary>

```bash
# Using Homebrew
brew install kubectl

# Verify
kubectl version --client
```

</details>

<details>
<summary>🐧 Linux</summary>

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify
kubectl version --client
```

</details>

### Install kind (Kubernetes in Docker)

**kind** runs a Kubernetes cluster inside Docker - perfect for learning!

<details>
<summary>🪟 Windows</summary>

```powershell
# Using Chocolatey
choco install kind

# Or direct download
curl -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.20.0/kind-windows-amd64
# Rename to kind.exe and move to PATH
```

</details>

<details>
<summary>🍎 Mac</summary>

```bash
brew install kind
```

</details>

<details>
<summary>🐧 Linux</summary>

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

</details>

### Create a Local Cluster

```bash
# Create cluster
kind create cluster --name k8s-challenge

# Verify it's running
kubectl cluster-info
kubectl get nodes
```

You should see:
```
NAME                          STATUS   ROLES           AGE
k8s-challenge-control-plane   Ready    control-plane   1m
```

✅ **Checkpoint:** kubectl and kind are working

---

## Step 1: Understand Kubernetes Concepts

Before writing manifests, let's understand the building blocks.

### Core Concepts

| Concept | What It Is | Analogy |
|---------|-----------|---------|
| **Pod** | Smallest deployable unit (1+ containers) | A single instance of your app |
| **Deployment** | Manages multiple Pods | "I want 3 copies running" |
| **Service** | Network endpoint for Pods | "Connect to the app on port 80" |
| **ConfigMap** | Non-sensitive configuration | "Here are the settings" |
| **Secret** | Sensitive data (passwords, API keys) | "Here's the password (encrypted)" |

### How They Connect

```
                     Internet
                         │
                         ▼
                   ┌──────────┐
                   │ Service  │  ← Network endpoint
                   └────┬─────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐
    │  Pod 1  │   │  Pod 2  │   │  Pod 3  │  ← Running containers
    └─────────┘   └─────────┘   └─────────┘
         │              │              │
         └──────────────┴──────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
    ┌─────────┐                  ┌───────────┐
    │ConfigMap│                  │  Secret   │
    │ (config)│                  │ (API key) │
    └─────────┘                  └───────────┘
```

### YAML Structure

Kubernetes uses YAML files called "manifests":

```yaml
apiVersion: v1              # API version
kind: Pod                   # What type of resource
metadata:
  name: my-pod              # Name of this resource
  labels:                   # Labels for selection
    app: myapp
spec:                       # The actual specification
  containers:
    - name: mycontainer
      image: nginx
```

---

## Step 2: Create a Deployment

> ⏱️ **Time:** 30-40 minutes

### What is a Deployment?

A Deployment tells Kubernetes:
- What container image to run
- How many copies (replicas)
- How to update (rolling update strategy)
- What resources to allocate

### Your Task

Create `k8s/deployment.yaml`:

**Requirements:**
- [ ] Use the `k8s-challenge-app:latest` image
- [ ] Run 2 replicas minimum
- [ ] Set resource limits (CPU and memory)
- [ ] Add liveness and readiness probes
- [ ] Use labels for selection

### Step-by-Step Guide

<details>
<summary>💡 Hint 1: Basic Structure</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: k8s-challenge-app:latest
          ports:
            - containerPort: 5000
```

</details>

<details>
<summary>💡 Hint 2: Resource Limits</summary>

Always set resource limits to prevent runaway containers:

```yaml
containers:
  - name: myapp
    resources:
      requests:           # Minimum needed
        memory: "64Mi"
        cpu: "100m"       # 100 millicores = 0.1 CPU
      limits:             # Maximum allowed
        memory: "128Mi"
        cpu: "200m"
```

</details>

<details>
<summary>💡 Hint 3: Health Checks (Probes)</summary>

**Liveness probe:** Is the container alive? (restart if not)
**Readiness probe:** Is it ready for traffic? (remove from load balancer if not)

```yaml
containers:
  - name: myapp
    livenessProbe:
      httpGet:
        path: /health
        port: 5000
      initialDelaySeconds: 10
      periodSeconds: 30

    readinessProbe:
      httpGet:
        path: /health
        port: 5000
      initialDelaySeconds: 5
      periodSeconds: 10
```

</details>

<details>
<summary>💡 Hint 4: Environment Variables from ConfigMap/Secret</summary>

```yaml
containers:
  - name: myapp
    env:
      - name: APP_ENV
        valueFrom:
          configMapKeyRef:
            name: myapp-config
            key: environment
      - name: API_KEY
        valueFrom:
          secretKeyRef:
            name: myapp-secrets
            key: api-key
```

</details>

<details>
<summary>🎯 Full Solution</summary>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k8s-challenge-app
  labels:
    app: k8s-challenge
spec:
  replicas: 2
  selector:
    matchLabels:
      app: k8s-challenge
  template:
    metadata:
      labels:
        app: k8s-challenge
    spec:
      containers:
        - name: app
          image: k8s-challenge-app:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
              name: http

          # Environment from ConfigMap
          envFrom:
            - configMapRef:
                name: k8s-challenge-config

          # Environment from Secret
          env:
            - name: API_KEY
              valueFrom:
                secretKeyRef:
                  name: k8s-challenge-secrets
                  key: api-key

          # Resource limits
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "200m"

          # Liveness probe - restart if unhealthy
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 3
            failureThreshold: 3

          # Readiness probe - remove from service if not ready
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
```

</details>

---

## Step 3: Create a Service

> ⏱️ **Time:** 15-20 minutes

### What is a Service?

Pods get random IP addresses that change when they restart. A Service provides a stable endpoint.

### Service Types

| Type | Use Case | Access |
|------|----------|--------|
| **ClusterIP** | Internal only | Within cluster |
| **NodePort** | Development | localhost:30000+ |
| **LoadBalancer** | Production (cloud) | External IP |

### Your Task

Create `k8s/service.yaml`:

<details>
<summary>💡 Hint: Service Structure</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  type: NodePort        # Or ClusterIP for internal
  selector:
    app: myapp          # Must match Pod labels!
  ports:
    - port: 80          # Service port
      targetPort: 5000  # Container port
      nodePort: 30080   # External port (NodePort only)
```

</details>

<details>
<summary>🎯 Full Solution</summary>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: k8s-challenge-service
  labels:
    app: k8s-challenge
spec:
  type: NodePort
  selector:
    app: k8s-challenge    # Must match Deployment labels!
  ports:
    - name: http
      port: 80            # Service port
      targetPort: 5000    # Container port
      nodePort: 30080     # External access port
      protocol: TCP
```

</details>

---

## Step 4: Create ConfigMap and Secret

> ⏱️ **Time:** 20-25 minutes

### ConfigMap vs Secret

| ConfigMap | Secret |
|-----------|--------|
| Non-sensitive config | Sensitive data |
| Stored as plain text | Base64 encoded |
| Environment variables, files | Passwords, API keys, certs |

### Your Task

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: k8s-challenge-config
data:
  FLASK_ENV: "production"
  LOG_LEVEL: "INFO"
  APP_NAME: "K8s Challenge App"
```

Create `k8s/secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: k8s-challenge-secrets
type: Opaque
data:
  # Values must be base64 encoded!
  # echo -n "your-api-key" | base64
  api-key: eW91ci1hcGkta2V5  # "your-api-key" in base64
```

**Important:** In real projects, NEVER commit actual secrets to git!

---

## Step 5: Deploy and Test

### Build the App Image

First, build the Docker image and load it into kind:

```bash
# Build the image
docker build -t k8s-challenge-app:latest ./src

# Load into kind cluster
kind load docker-image k8s-challenge-app:latest --name k8s-challenge
```

### Apply Manifests

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services
kubectl get deployments
```

### Test the Application

```bash
# Port forward to access locally
kubectl port-forward service/k8s-challenge-service 8080:80

# In another terminal, test the app
curl http://localhost:8080/health
```

### Debugging Commands

```bash
# View pod logs
kubectl logs -l app=k8s-challenge

# Describe a pod (see events, errors)
kubectl describe pod <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Watch pods in real-time
kubectl get pods -w
```

---

## Step 6: Run Tests & Submit

### Local Testing

```bash
python run.py
```

### Submit to GitHub

```bash
git add .
git commit -m "Complete Kubernetes challenge"
git push origin main
```

---

## Understanding Kubernetes (For DevOps Students)

### Key Concepts You Learned

| Concept | What You Now Understand |
|---------|------------------------|
| **Pod** | Smallest unit, runs containers |
| **Deployment** | Manages replicas, rolling updates |
| **Service** | Stable networking endpoint |
| **ConfigMap** | Externalized configuration |
| **Secret** | Secure sensitive data |
| **Labels** | How resources find each other |
| **Probes** | Health monitoring |
| **Resources** | CPU/memory management |

### kubectl Cheat Sheet

```bash
# Get resources
kubectl get pods                    # List pods
kubectl get pods -o wide            # More details
kubectl get all                     # All resources
kubectl get pods -w                 # Watch mode

# Describe (detailed info)
kubectl describe pod <name>
kubectl describe deployment <name>

# Logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>          # Follow logs
kubectl logs -l app=myapp           # By label

# Execute commands
kubectl exec -it <pod> -- /bin/sh   # Shell into pod
kubectl exec <pod> -- ls /app       # Run command

# Apply/Delete
kubectl apply -f file.yaml          # Create/update
kubectl delete -f file.yaml         # Delete
kubectl delete pod <name>           # Delete specific

# Debug
kubectl get events                  # Recent events
kubectl top pods                    # Resource usage
```

### What You Can Say in Interviews

> "I deployed a containerized application to Kubernetes with 2 replicas for high availability. I configured a Deployment with resource limits and health checks (liveness/readiness probes), exposed it via a Service, and managed configuration through ConfigMaps and Secrets. I understand how Kubernetes handles rolling updates, self-healing, and load balancing."

---

## Troubleshooting

<details>
<summary>❌ Pods stuck in "Pending"</summary>

Usually means insufficient resources. Check:
```bash
kubectl describe pod <name>
# Look for "Events" section
```

</details>

<details>
<summary>❌ Pods in "CrashLoopBackOff"</summary>

Container keeps crashing. Check logs:
```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

</details>

<details>
<summary>❌ Service not accessible</summary>

1. Check selector matches pod labels
2. Check pods are running: `kubectl get pods`
3. Check endpoints: `kubectl get endpoints`

</details>

<details>
<summary>❌ Image pull errors</summary>

For kind, load images first:
```bash
kind load docker-image myimage:tag --name k8s-challenge
```

</details>

---

## Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Delete the cluster
kind delete cluster --name k8s-challenge
```

---

## What You Learned

- ✅ **Kubernetes basics** - Pods, Deployments, Services
- ✅ **YAML manifests** - Declarative configuration
- ✅ **Config management** - ConfigMaps and Secrets
- ✅ **Health checks** - Liveness and readiness probes
- ✅ **Resource limits** - CPU and memory management
- ✅ **kubectl** - Command-line operations

---

## Next Steps

- **3.1 Monitoring Stack** - Add Prometheus and Grafana
- **2.1 Terraform Basics** - Infrastructure as Code

Good luck! ☸️
