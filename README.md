# GCP CI/CD and GitOps Portfolio Project

End-to-end DevOps portfolio project on Google Cloud using GKE Standard, Terraform, GitHub Actions, Docker Hub, ArgoCD, Prometheus, and Grafana.

The project demonstrates a practical delivery workflow from code commit to monitored Kubernetes rollout. A Flask DevOps dashboard runs on GKE and exposes health, readiness, metrics, and runtime metadata so each release can be verified after deployment.

## Project Summary

The goal was to build a realistic DevOps workflow, not only a sample web app.

The implementation covers:

- Infrastructure provisioning on Google Cloud.
- Docker image build and publishing through GitHub Actions.
- GitOps-based delivery with ArgoCD.
- Kubernetes readiness, liveness, replicas, and resource controls.
- Runtime release visibility through Git SHA and image version.
- Prometheus metrics and Grafana dashboards for operational visibility.
- Public access through a GKE LoadBalancer service with static IP and custom domain support.

## Current Status

| Area | Current state |
| --- | --- |
| Cloud platform | Google Cloud Platform |
| Kubernetes | GKE Standard |
| Application | Flask DevOps dashboard |
| Deployment | `simple-api` |
| Replicas | 3 |
| Service | `simple-app-svc` |
| Exposure | GKE LoadBalancer with static IP configured for custom domain |
| GitOps | ArgoCD syncs plain Kubernetes manifests from `gitops-repo` |
| CI/CD | GitHub Actions builds image, pushes to Docker Hub, and updates `deployment.yaml` |
| Monitoring | Prometheus metrics exposed from the app and visualized through existing Grafana dashboards |

## Architecture

![GCP CI/CD and GitOps Architecture](https://github.com/Ali-chitsazan/GCP-CICD/blob/main/gitops-repo/xdiagram.drawio.png)

### Validated Flow

1. A developer pushes changes to GitHub.
2. GitHub Actions runs on the `main` branch.
3. The workflow builds the Docker image from `app-repo`.
4. The image is tagged with the Git commit SHA.
5. The image is pushed to Docker Hub.
6. The workflow updates the image field in `gitops-repo/deployment.yaml`.
7. The manifest update is committed back to Git.
8. ArgoCD watches the `gitops-repo` path.
9. ArgoCD compares Git desired state with the live GKE cluster.
10. ArgoCD syncs the application into Kubernetes.
11. GKE rolls out the `simple-api` pods using readiness and liveness probes.
12. Prometheus scrapes the application metrics endpoint.
13. Grafana dashboards show release health, readiness, traffic, and unexpected request paths.

### Validation Notes

- ArgoCD syncs plain Kubernetes manifests from `gitops-repo`.
- Kustomize is not used in the current implementation.
- The application listens on port 5000.
- The Kubernetes Service exposes port 80 and routes traffic to targetPort 5000.
- Static IP has been added for custom domain usage.
- HTTPS/TLS should only be claimed when the domain is configured with a certificate through Ingress, Gateway API, managed certificate, or another TLS layer.

## Application Dashboard

The running application provides a browser-based release verification page.

![GCP CI/CD Demo App Dashboard]([https://github.com/Ali-chitsazan/GCP-CICD/blob/main/gitops-repo/xapp.png])

The dashboard shows:

- Environment.
- Image version.
- Git SHA.
- Pod name.
- Namespace.
- Node name.
- Python version.
- Uptime.
- Readiness state.
- Links to health, readiness, metrics, and API info endpoints.

This makes each release easier to verify because the deployed version can be traced back to the Git commit, image tag, and running Kubernetes pod.

## Repository Structure

```text
app-repo/
  Flask application source code, Dockerfile, requirements, and runtime logic.

app-repo/src/app.py
  Main Flask application with dashboard, health, readiness, metrics, and API info endpoints.

gitops-repo/deployment.yaml
  Kubernetes Deployment for simple-api. CI updates the image tag here.

gitops-repo/service.yaml
  Kubernetes LoadBalancer Service for public access.

argocd/apps/simple-api.yaml
  ArgoCD Application pointing to gitops-repo.

.github/workflows/ci.yaml
  GitHub Actions workflow for Docker build, Docker Hub push, and GitOps manifest update.

terraform/
  Infrastructure provisioning for GCP networking, GKE, and related platform setup.
```

## Technology Stack

| Area | Tools |
| --- | --- |
| Cloud and infrastructure | GCP, GKE Standard, Terraform, VPC, subnet, node pool, static IP |
| CI/CD | GitHub Actions, Docker Hub, GitHub repository secrets |
| GitOps | ArgoCD, plain Kubernetes manifests, Git desired state |
| Application runtime | Python, Flask, Docker, Kubernetes Deployment and Service |
| Kubernetes operations | readiness probe, liveness probe, replicas, resource requests and limits |
| Observability | Prometheus metrics, Grafana dashboards, application request counters and latency metrics |

## Application Endpoints

| Endpoint | Purpose |
| --- | --- |
| `/` | Main DevOps dashboard with release and runtime metadata |
| `/health` | Liveness endpoint used by Kubernetes |
| `/ready` | Readiness endpoint used before routing traffic to pods |
| `/metrics` | Prometheus-format application metrics |
| `/api/info` | JSON response with release and runtime details |

## Kubernetes Runtime

| Item | Current setup |
| --- | --- |
| Deployment name | `simple-api` |
| Replica count | 3 |
| Container port | 5000 |
| Service name | `simple-app-svc` |
| Service type | `LoadBalancer` |
| Service port | 80 |
| Service targetPort | 5000 |
| Readiness probe | `/ready` on port 5000 |
| Liveness probe | `/health` on port 5000 |
| CPU request / limit | 50m / 100m |
| Memory request / limit | 128Mi / 256Mi |
| Release metadata | Image version and Git SHA |

Readiness and liveness probes make rollout behavior visible. A pod can be running but not ready, and the Service should only send traffic to ready pods.

## CI/CD Workflow

GitHub Actions handles the build and GitOps update process.

- Runs on push to `main`.
- Ignores `gitops-repo/**` changes to prevent CI loops.
- Authenticates to Docker Hub through GitHub secrets.
- Builds the Docker image from `./app-repo`.
- Passes `IMAGE_VERSION` and `GIT_SHA` as Docker build arguments.
- Tags the image with the Git commit SHA.
- Pushes the image to Docker Hub.
- Updates the image field in `gitops-repo/deployment.yaml`.
- Commits the manifest change back to the repository only when the image tag changed.

This creates traceability from source code to Docker image to Kubernetes deployment.

## GitOps with ArgoCD

ArgoCD handles the delivery side.

The `simple-api` ArgoCD Application:

- Points to the same GitHub repository.
- Tracks the `main` branch.
- Uses `gitops-repo` as the desired-state path.
- Deploys to the `default` namespace.
- Uses automated sync.
- Uses prune to remove resources deleted from Git.
- Uses self-healing to correct manual drift.
- Uses `CreateNamespace=true` when needed.

This separates build logic from deployment logic. GitHub Actions creates the release artifact and updates Git. ArgoCD applies the desired state to the cluster.

## Observability

The app exposes Prometheus-format metrics through `/metrics`.

Existing Grafana dashboards are used to monitor:

- Release health.
- Pod readiness.
- Replica availability.
- HTTP request volume.
- Endpoint-level traffic.
- Unexpected request paths.
- Suspicious public scan traffic.

The unexpected request panels are useful because public LoadBalancer endpoints often receive automated internet scans. Tracking those paths turns the demo into a stronger security-observability story.

## Problems Solved

This project includes real troubleshooting across the DevOps workflow.

- Fixed Docker build and runtime path issues so the container runs the correct Flask source file.
- Added release metadata so the running app shows image version and Git SHA.
- Resolved Service routing by matching Service targetPort with Flask port 5000.
- Prevented GitHub Actions loops caused by GitOps commits.
- Resolved local and remote Git branch divergence with a safer rebase workflow.
- Validated image tag propagation from GitHub Actions to Kubernetes manifests.
- Troubleshot ArgoCD sync behavior when Git and cluster state appeared synced but pods did not change.
- Tested Kubernetes readiness, liveness, pending pods, and resource pressure behavior.
- Retrieved current Grafana credentials from Kubernetes secrets instead of relying on old passwords.
- Improved dashboard focus around release health and unexpected traffic instead of adding too many panels.

## Useful Commands

Check services:

```bash
kubectl get svc
kubectl get svc simple-app-svc
```

Check rollout status:

```bash
kubectl rollout status deploy/simple-api
kubectl get pods -o wide
```

Inspect a failing pod:

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

Port-forward the application:

```bash
kubectl port-forward svc/simple-app-svc 8080:80
```

Check CPU requests and limits:

```bash
kubectl get deploy simple-api -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{" cpu-request="}{.resources.requests.cpu}{" cpu-limit="}{.resources.limits.cpu}{"\n"}{end}'
```

Retrieve the Grafana admin password:

```bash
kubectl -n monitoring get secret monitoring-grafana -o jsonpath='{.data.admin-password}' | base64 -d
```

Safe Git workflow before pushing changes:

```bash
git status
git pull origin main --rebase
git push origin main
```

## Business Value

- Reduces manual deployment work through automated image build, image publishing, and GitOps delivery.
- Improves traceability by linking each deployment to a Git commit SHA.
- Improves reliability with replicas, readiness probes, liveness probes, and ArgoCD self-healing.
- Improves troubleshooting with runtime metadata, application metrics, and dashboard visibility.
- Improves operational awareness by tracking release health, traffic, pod readiness, and unexpected paths.
- Adds a realistic security-observability example by showing scan traffic against a public endpoint.

## Pending Improvements / Optimization

1. Integrate AI-assisted Kubernetes troubleshooting using K8sGPT or a similar tool.
2. Optimize existing Grafana dashboards for release health, pod readiness, traffic, 5xx errors, and unexpected paths.
3. Add alert rules for not-ready pods, unavailable deployments, high error rates, and suspicious request spikes.
4. Version-control Grafana dashboard JSON so dashboards can be rebuilt consistently.
5. Add a test stage before Docker image build.
6. Add container image scanning and dependency checks to CI.
7. Add or finalize HTTPS/TLS for the custom domain if not already completed.
8. Define clearer dev/prod promotion rules using separate manifest paths.
