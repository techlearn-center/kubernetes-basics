#!/usr/bin/env python3
"""
Kubernetes Challenge Runner
============================
Run this script to check your Kubernetes manifests and see your progress.

Usage:
    python run.py          # Check all manifests
    python run.py --deploy # Deploy to kind cluster and test
    python run.py --clean  # Clean up resources
"""

import subprocess
import sys
import os
import re
import yaml
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

# For Windows compatibility
if sys.platform == 'win32':
    os.system('color')  # Enable ANSI colors on Windows


def print_header():
    """Print the challenge header."""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  ☸️  Kubernetes Basics Challenge{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")


def load_yaml_file(file_path):
    """Load and parse a YAML file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return None
    except yaml.YAMLError as e:
        return {"error": str(e)}


def check_deployment(manifest):
    """Check deployment manifest for required elements."""
    checks = []
    points = 0
    max_points = 25

    if manifest is None:
        return [("Deployment file exists", False, "File not found")], 0, max_points

    if "error" in manifest:
        return [("Valid YAML", False, manifest["error"])], 0, max_points

    # Check replicas
    replicas = manifest.get("spec", {}).get("replicas", 0)
    if replicas >= 2:
        checks.append(("Replicas >= 2", True, f"Found {replicas} replicas"))
        points += 5
    else:
        checks.append(("Replicas >= 2", False, f"Found {replicas}, need at least 2"))

    # Check container spec
    containers = manifest.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    if containers:
        container = containers[0]

        # Check image
        image = container.get("image", "")
        if "k8s-challenge-app" in image:
            checks.append(("Correct image", True, image))
            points += 3
        else:
            checks.append(("Correct image", False, f"Expected k8s-challenge-app, got {image}"))

        # Check resource limits
        resources = container.get("resources", {})
        if resources.get("limits") and resources.get("requests"):
            checks.append(("Resource limits", True, "Requests and limits defined"))
            points += 5
        else:
            checks.append(("Resource limits", False, "Missing requests or limits"))

        # Check liveness probe
        if container.get("livenessProbe"):
            probe = container["livenessProbe"]
            if probe.get("httpGet", {}).get("path") == "/health":
                checks.append(("Liveness probe", True, "HTTP GET /health"))
                points += 4
            else:
                checks.append(("Liveness probe", False, "Wrong path or type"))
        else:
            checks.append(("Liveness probe", False, "Not configured"))

        # Check readiness probe
        if container.get("readinessProbe"):
            probe = container["readinessProbe"]
            if probe.get("httpGet", {}).get("path") == "/health":
                checks.append(("Readiness probe", True, "HTTP GET /health"))
                points += 4
            else:
                checks.append(("Readiness probe", False, "Wrong path or type"))
        else:
            checks.append(("Readiness probe", False, "Not configured"))

        # Check env/envFrom
        has_configmap = False
        has_secret = False

        if container.get("envFrom"):
            for env in container["envFrom"]:
                if env.get("configMapRef"):
                    has_configmap = True

        if container.get("env"):
            for env in container["env"]:
                if env.get("valueFrom", {}).get("secretKeyRef"):
                    has_secret = True

        if has_configmap:
            checks.append(("ConfigMap reference", True, "envFrom configured"))
            points += 2
        else:
            checks.append(("ConfigMap reference", False, "Missing envFrom configMapRef"))

        if has_secret:
            checks.append(("Secret reference", True, "secretKeyRef configured"))
            points += 2
        else:
            checks.append(("Secret reference", False, "Missing secretKeyRef"))

    else:
        checks.append(("Container defined", False, "No containers found"))

    return checks, points, max_points


def check_service(manifest):
    """Check service manifest for required elements."""
    checks = []
    points = 0
    max_points = 20

    if manifest is None:
        return [("Service file exists", False, "File not found")], 0, max_points

    if "error" in manifest:
        return [("Valid YAML", False, manifest["error"])], 0, max_points

    # Check type
    svc_type = manifest.get("spec", {}).get("type", "ClusterIP")
    if svc_type == "NodePort":
        checks.append(("Service type", True, "NodePort"))
        points += 5
    else:
        checks.append(("Service type", False, f"Expected NodePort, got {svc_type}"))

    # Check selector
    selector = manifest.get("spec", {}).get("selector", {})
    if selector.get("app") == "k8s-challenge":
        checks.append(("Selector matches", True, "app: k8s-challenge"))
        points += 5
    else:
        checks.append(("Selector matches", False, f"Expected app: k8s-challenge, got {selector}"))

    # Check ports
    ports = manifest.get("spec", {}).get("ports", [])
    if ports:
        port = ports[0]
        if port.get("port") == 80 and port.get("targetPort") == 5000:
            checks.append(("Port mapping", True, "80 → 5000"))
            points += 5
        else:
            checks.append(("Port mapping", False, f"Expected 80→5000, got {port.get('port')}→{port.get('targetPort')}"))

        if port.get("nodePort"):
            checks.append(("NodePort set", True, f"Port {port['nodePort']}"))
            points += 5
        else:
            checks.append(("NodePort set", False, "Not specified"))
    else:
        checks.append(("Ports defined", False, "No ports configured"))

    return checks, points, max_points


def check_configmap(manifest):
    """Check configmap manifest for required elements."""
    checks = []
    points = 0
    max_points = 15

    if manifest is None:
        return [("ConfigMap file exists", False, "File not found")], 0, max_points

    if "error" in manifest:
        return [("Valid YAML", False, manifest["error"])], 0, max_points

    # Check name
    name = manifest.get("metadata", {}).get("name", "")
    if name == "k8s-challenge-config":
        checks.append(("Correct name", True, name))
        points += 3
    else:
        checks.append(("Correct name", False, f"Expected k8s-challenge-config, got {name}"))

    # Check data
    data = manifest.get("data", {})

    # Remove placeholder
    if "PLACEHOLDER" in data:
        checks.append(("Remove placeholder", False, "PLACEHOLDER key still present"))
    else:
        points += 2

    required_keys = ["FLASK_ENV", "LOG_LEVEL", "APP_NAME"]
    found_keys = []
    for key in required_keys:
        if key in data:
            found_keys.append(key)

    if len(found_keys) == len(required_keys):
        checks.append(("All config keys", True, ", ".join(found_keys)))
        points += 10
    else:
        missing = set(required_keys) - set(found_keys)
        checks.append(("All config keys", False, f"Missing: {', '.join(missing)}"))
        points += len(found_keys) * 3  # Partial credit

    return checks, points, max_points


def check_secret(manifest):
    """Check secret manifest for required elements."""
    checks = []
    points = 0
    max_points = 15

    if manifest is None:
        return [("Secret file exists", False, "File not found")], 0, max_points

    if "error" in manifest:
        return [("Valid YAML", False, manifest["error"])], 0, max_points

    # Check name
    name = manifest.get("metadata", {}).get("name", "")
    if name == "k8s-challenge-secrets":
        checks.append(("Correct name", True, name))
        points += 3
    else:
        checks.append(("Correct name", False, f"Expected k8s-challenge-secrets, got {name}"))

    # Check type
    secret_type = manifest.get("type", "")
    if secret_type == "Opaque":
        checks.append(("Type Opaque", True, ""))
        points += 2
    else:
        checks.append(("Type Opaque", False, f"Got {secret_type}"))

    # Check api-key
    data = manifest.get("data", {})
    api_key = data.get("api-key", "")

    if api_key and api_key != "REPLACE-WITH-BASE64-ENCODED-VALUE":
        # Try to validate it's base64
        import base64
        try:
            decoded = base64.b64decode(api_key).decode('utf-8')
            if len(decoded) > 0:
                checks.append(("api-key (base64)", True, f"Valid ({len(decoded)} chars decoded)"))
                points += 10
            else:
                checks.append(("api-key (base64)", False, "Empty value"))
        except:
            checks.append(("api-key (base64)", False, "Invalid base64 encoding"))
    else:
        checks.append(("api-key (base64)", False, "Not set or still placeholder"))

    return checks, points, max_points


def check_all_manifests():
    """Check all Kubernetes manifests."""
    print_header()
    print(f"  {Colors.BOLD}Checking your Kubernetes manifests...{Colors.END}\n")

    k8s_dir = Path(__file__).parent / "k8s"

    total_points = 0
    max_total = 0

    checks_by_file = [
        ("deployment.yaml", "Deployment", check_deployment, 25),
        ("service.yaml", "Service", check_service, 20),
        ("configmap.yaml", "ConfigMap", check_configmap, 15),
        ("secret.yaml", "Secret", check_secret, 15),
    ]

    for filename, display_name, check_func, max_pts in checks_by_file:
        file_path = k8s_dir / filename
        manifest = load_yaml_file(file_path)
        checks, points, max_points = check_func(manifest)

        total_points += points
        max_total += max_points

        # Print results
        status_icon = f"{Colors.GREEN}✅{Colors.END}" if points == max_points else f"{Colors.YELLOW}⏳{Colors.END}"
        print(f"  {status_icon} {Colors.BOLD}{display_name}{Colors.END} ({points}/{max_points} points)")

        for check_name, passed, detail in checks:
            icon = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
            detail_str = f" - {detail}" if detail else ""
            print(f"      {icon} {check_name}{detail_str}")

        print()

    # Progress bar
    progress_pct = int((total_points / max_total) * 100) if max_total > 0 else 0
    bar_filled = int(progress_pct / 5)
    bar_empty = 20 - bar_filled

    bar_color = Colors.GREEN if progress_pct >= 80 else Colors.YELLOW
    print(f"  {Colors.BOLD}Score:{Colors.END}")
    print(f"  {bar_color}{'█' * bar_filled}{'░' * bar_empty}{Colors.END} {total_points}/{max_total} points ({progress_pct}%)")

    if progress_pct == 100:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}🎉 All manifests complete!{Colors.END}")
        print(f"  {Colors.CYAN}Run 'python run.py --deploy' to test in a real cluster!{Colors.END}")
    elif progress_pct >= 80:
        print(f"\n  {Colors.GREEN}Almost there! Check the items marked with ✗{Colors.END}")
    else:
        print(f"\n  {Colors.CYAN}Keep going! See README.md for guidance.{Colors.END}")

    print()
    return progress_pct == 100


def check_kubectl():
    """Check if kubectl is installed."""
    try:
        result = subprocess.run(
            ["kubectl", "version", "--client", "--short"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def check_kind():
    """Check if kind is installed."""
    try:
        result = subprocess.run(
            ["kind", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def check_docker():
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


def deploy_to_cluster():
    """Deploy manifests to kind cluster and test."""
    print_header()
    print(f"  {Colors.BOLD}Deploying to Kubernetes cluster...{Colors.END}\n")

    # Check prerequisites
    print(f"  {Colors.CYAN}Checking prerequisites...{Colors.END}")

    if not check_docker():
        print(f"  {Colors.RED}❌ Docker is not running{Colors.END}")
        print(f"  {Colors.YELLOW}Start Docker Desktop and try again.{Colors.END}\n")
        return

    if not check_kubectl():
        print(f"  {Colors.RED}❌ kubectl not found{Colors.END}")
        print(f"  {Colors.YELLOW}See README.md Step 0 to install kubectl.{Colors.END}\n")
        return

    if not check_kind():
        print(f"  {Colors.RED}❌ kind not found{Colors.END}")
        print(f"  {Colors.YELLOW}See README.md Step 0 to install kind.{Colors.END}\n")
        return

    print(f"  {Colors.GREEN}✓ All tools available{Colors.END}\n")

    # Check/create cluster
    print(f"  {Colors.CYAN}Checking kind cluster...{Colors.END}")
    result = subprocess.run(
        ["kind", "get", "clusters"],
        capture_output=True,
        text=True
    )

    if "k8s-challenge" not in result.stdout:
        print(f"  {Colors.YELLOW}Creating kind cluster 'k8s-challenge'...{Colors.END}")
        result = subprocess.run(
            ["kind", "create", "cluster", "--name", "k8s-challenge"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  {Colors.RED}❌ Failed to create cluster{Colors.END}")
            print(result.stderr)
            return
        print(f"  {Colors.GREEN}✓ Cluster created{Colors.END}")
    else:
        print(f"  {Colors.GREEN}✓ Cluster exists{Colors.END}")

    # Build and load image
    print(f"\n  {Colors.CYAN}Building Docker image...{Colors.END}")
    src_dir = Path(__file__).parent / "src"
    result = subprocess.run(
        ["docker", "build", "-t", "k8s-challenge-app:latest", str(src_dir)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  {Colors.RED}❌ Failed to build image{Colors.END}")
        print(result.stderr)
        return
    print(f"  {Colors.GREEN}✓ Image built{Colors.END}")

    print(f"  {Colors.CYAN}Loading image into kind...{Colors.END}")
    result = subprocess.run(
        ["kind", "load", "docker-image", "k8s-challenge-app:latest", "--name", "k8s-challenge"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  {Colors.RED}❌ Failed to load image{Colors.END}")
        print(result.stderr)
        return
    print(f"  {Colors.GREEN}✓ Image loaded{Colors.END}")

    # Apply manifests
    print(f"\n  {Colors.CYAN}Applying Kubernetes manifests...{Colors.END}")
    k8s_dir = Path(__file__).parent / "k8s"
    result = subprocess.run(
        ["kubectl", "apply", "-f", str(k8s_dir)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  {Colors.RED}❌ Failed to apply manifests{Colors.END}")
        print(result.stderr)
        return

    for line in result.stdout.strip().split('\n'):
        print(f"      {line}")

    # Wait for deployment
    print(f"\n  {Colors.CYAN}Waiting for pods to be ready...{Colors.END}")
    result = subprocess.run(
        ["kubectl", "wait", "--for=condition=available", "deployment/k8s-challenge-app", "--timeout=60s"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"  {Colors.GREEN}✓ Deployment is ready!{Colors.END}")
    else:
        print(f"  {Colors.YELLOW}⏳ Deployment not ready yet{Colors.END}")
        print(f"  {Colors.YELLOW}Run 'kubectl get pods' to check status{Colors.END}")

    # Show status
    print(f"\n  {Colors.CYAN}Current status:{Colors.END}")
    subprocess.run(["kubectl", "get", "pods", "-l", "app=k8s-challenge"])
    print()
    subprocess.run(["kubectl", "get", "services", "-l", "app=k8s-challenge"])

    print(f"\n  {Colors.GREEN}{Colors.BOLD}🎉 Deployment complete!{Colors.END}")
    print(f"\n  {Colors.CYAN}To test your app:{Colors.END}")
    print(f"  kubectl port-forward service/k8s-challenge-service 8080:80")
    print(f"  curl http://localhost:8080/health")
    print(f"\n  {Colors.CYAN}To view logs:{Colors.END}")
    print(f"  kubectl logs -l app=k8s-challenge")
    print()


def cleanup():
    """Clean up resources."""
    print_header()
    print(f"  {Colors.BOLD}Cleaning up...{Colors.END}\n")

    # Delete resources
    print(f"  {Colors.CYAN}Deleting Kubernetes resources...{Colors.END}")
    k8s_dir = Path(__file__).parent / "k8s"
    subprocess.run(
        ["kubectl", "delete", "-f", str(k8s_dir), "--ignore-not-found"],
        capture_output=True
    )
    print(f"  {Colors.GREEN}✓ Resources deleted{Colors.END}")

    # Optionally delete cluster
    print(f"\n  {Colors.YELLOW}To delete the kind cluster:{Colors.END}")
    print(f"  kind delete cluster --name k8s-challenge")
    print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Kubernetes Challenge Runner")
    parser.add_argument("--deploy", action="store_true", help="Deploy to kind cluster")
    parser.add_argument("--clean", action="store_true", help="Clean up resources")

    args = parser.parse_args()

    os.chdir(Path(__file__).parent)

    if args.deploy:
        deploy_to_cluster()
    elif args.clean:
        cleanup()
    else:
        check_all_manifests()


if __name__ == "__main__":
    main()
