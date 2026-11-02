# Project Verification Tracking

| Phase | Deliverable | Command / Verification Check | Result / Evidence | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Prerequisites** | Minikube Installation | `minikube version` | minikube v1.39.0 installed | Verified |
| **Prerequisites** | Python Virtual Environment | `python -V` in `.venv` | Python 3.12.1 + pinned deps in requirements-dev.txt | Verified |
| **Phase 1** | Raw Dataset Ingestion | `python scripts/download_data.py` | 4,269 rows raw dataset ingested into data/raw/ | Verified |
| **Phase 1** | Exploratory Data Analysis | `notebooks/01_eda.ipynb` executed | Cleaned whitespace, class balance & CIBIL leak documented | Verified |
| **Phase 1** | ML Pipeline & Leakage Check | `python -m src.train` | Trained LR & RF; RF chosen (F1: 0.9822, AUC: 0.9964) | Verified |
| **Phase 1** | Metrics Artifact | Check `models/metrics.json` | JSON verified with metrics, confusion matrix & leakage notes | Verified |
| **Phase 1** | Trained Model Artifact | Check `models/loan_model.joblib` | Committed scikit-learn pipeline saved | Verified |
| **Phase 1** | Automated Unit Tests | `pytest tests/` | 10/10 tests passed; flake8 clean | Verified |
| **Phase 2** | Local Streamlit App (UI) | `streamlit run streamlit_app.py` or `python app.py` | UI with applicant presets, underwriting, explainability & health endpoint (HTTP 200) | Verified |
| **Phase 2** | Metrics Instrumentation | `curl http://localhost:8000/metrics` | Prometheus exporter running on port 8000; telemetry for predictions, latency, CIBIL, & amounts | Verified |
| **Phase 3** | Git Init & Secret Hygiene | `git status` / `git log` | Git initialized on `main`; comprehensive `.gitignore`; secret audit confirmed clean | Verified |
| **Phase 3** | GitHub Repository Connected | `git remote -v` & `git push` | Connected to `https://github.com/viraj0710/loan-approval-mlops.git`; branch `main` tracking and pushed | Verified |
| **Phase 4** | Docker Image Build | `docker build -t loan-approval-mlops .` | Multi-port container image built (`python:3.12-slim`, non-root `appuser`) | Verified |
| **Phase 4** | Docker Health & Metrics Check | `/_stcore/health` and `:8000/metrics` | Container passed `HEALTHCHECK` (status: `healthy`), `8501/_stcore/health` (200), `8000/metrics` (200) | Verified |
| **Phase 4** | Tag & GHCR Preparation | `docker images` | Tagged as `ghcr.io/viraj0710/loan-approval-mlops:latest` and `:v1.0.0` | Verified |
| **Phase 5** | GitHub Actions Workflow | `.github/workflows/ci-cd.yml` | Multi-stage pipeline: Flake8 linting, Pytest suite, Buildx GHCR publish, and container smoke test | Verified |
| **Phase 5** | Green CI/CD Run | GitHub Actions run status | Run ID 41428805001 concluded with success (Lint, Test, Build, Push, Smoke Test green) | Verified |
| **Phase 6** | Minikube App Deployment | `kubectl get pods -n loan-app` | Not Run | Not Run |
| **Phase 6** | Pod Recovery & Scaling | `kubectl scale ...` & pod recovery | Not Run | Not Run |
| **Phase 7** | Terraform Init, Plan & Apply | `terraform apply` | Not Run | Not Run |
| **Phase 7** | Terraform Destroy & Recreate | `terraform destroy` & re-apply | Not Run | Not Run |
| **Phase 8** | Prometheus Pod Discovery | Prometheus target status | Not Run | Not Run |
| **Phase 8** | Grafana Dashboard Verification | Dashboard metrics & screenshots | Not Run | Not Run |
| **Phase 9** | Public Streamlit Deployment | Streamlit Community Cloud URL check | Not Run | Not Run |
| **Final** | Complete README & Checklist | Document review | Not Run | Not Run |
