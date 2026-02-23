# DataPulse Analytics

**Real-time data analytics and AI-powered insights platform built with a microservices architecture.**

DataPulse Analytics is a production-grade, full-stack platform designed to ingest, process, analyze, and visualize high-volume data streams in real time. It combines multiple backend frameworks (Django, FastAPI, Flask), dual frontend applications (React, Angular), event-driven messaging (Kafka, RabbitMQ), AI-powered analysis (AWS Bedrock, OpenAI), and enterprise-grade infrastructure (Docker, Kubernetes, AWS, Azure).

---

## Architecture Overview

```
                    ┌──────────────────────────────────────────────┐
                    │              Load Balancer / Ingress          │
                    └──────────┬───────────┬───────────┬───────────┘
                               │           │           │
                    ┌──────────▼──┐  ┌─────▼─────┐  ┌─▼──────────┐
                    │  Django API  │  │  FastAPI   │  │  Flask AI   │
                    │  (Port 8000) │  │ Ingestion  │  │  Service    │
                    │  Main API    │  │ (Port 8001)│  │ (Port 5001) │
                    └──────┬──────┘  └─────┬──────┘  └──────┬─────┘
                           │               │                │
              ┌────────────┼───────────────┼────────────────┤
              │            │               │                │
        ┌─────▼────┐ ┌────▼─────┐  ┌──────▼──────┐  ┌─────▼──────┐
        │PostgreSQL │ │ MongoDB  │  │Elasticsearch│  │   Redis    │
        │  (SQL)    │ │ (NoSQL)  │  │  (Search)   │  │  (Cache)   │
        └──────────┘ └──────────┘  └─────────────┘  └────────────┘
              │            │               │
        ┌─────▼────────────▼───────────────▼─────┐
        │         Kafka / RabbitMQ               │
        │      (Event-Driven Messaging)          │
        └────────────────────────────────────────┘
              │                        │
        ┌─────▼──────┐         ┌──────▼──────┐
        │ AWS Lambda  │         │ Celery      │
        │ (Serverless)│         │ Workers     │
        └─────────────┘         └─────────────┘
```

## Tech Stack

| Category | Technologies |
|---|---|
| **UI Development** | React 18, Angular 17, Material UI, Angular Material |
| **Backend** | Python 3.11, Django 4.2, Flask 3.0, FastAPI 0.109 |
| **Messaging** | Apache Kafka, RabbitMQ, Celery |
| **CI/CD** | GitHub Actions, Jenkins |
| **Logging & Monitoring** | Datadog, ELK Stack (Elasticsearch, Logstash, Kibana), Grafana |
| **Databases** | PostgreSQL 16 (SQL), MongoDB 7 (NoSQL), Redis 7 (Cache) |
| **Search & Analytics** | Elasticsearch 8.12 |
| **Containerization** | Docker, Kubernetes (EKS/AKS), Helm |
| **Cloud** | AWS (EC2, S3, Lambda, EKS, RDS, ElastiCache), Azure (AKS, ACR, PostgreSQL) |
| **AI & LLM** | AWS Bedrock (Claude), OpenAI GPT-4 |
| **Version Control** | GitHub, Bitbucket |
| **Code Quality** | SonarQube |
| **Security** | Veracode |

## Project Structure

```
datapulse-analytics/
├── backend/
│   ├── django_app/              # Main API service (Django REST Framework)
│   │   ├── core/                # Django project settings, URLs, WSGI/ASGI
│   │   ├── analytics/           # Analytics app (models, views, serializers, tasks)
│   │   │   └── services/        # Kafka, Elasticsearch, MongoDB, S3 integrations
│   │   └── users/               # User management, JWT auth, profiles
│   ├── fastapi_service/         # High-performance ingestion service
│   │   └── app/
│   │       ├── routers/         # Ingestion, search, WebSocket endpoints
│   │       └── services/        # Kafka producer/consumer, ES client
│   └── flask_ai_service/        # AI/LLM integration service
│       └── app/
│           ├── routes/          # AI summarization, analysis, NL query endpoints
│           └── services/        # Bedrock, OpenAI, LLM orchestrator
├── frontend/
│   ├── react-dashboard/         # Main user dashboard (React + MUI + Recharts)
│   │   └── src/
│   │       ├── components/      # Layout, ProtectedRoute
│   │       ├── pages/           # Dashboard, Events, Alerts, Reports, AI Insights
│   │       ├── services/        # API client, WebSocket service
│   │       └── context/         # Auth context
│   └── angular-admin/           # Admin panel (Angular + Angular Material)
│       └── src/app/
│           ├── components/      # Admin dashboard, user management, system health
│           └── services/        # Admin API service, auth interceptor
├── infrastructure/
│   ├── docker/                  # Dockerfiles for all services
│   ├── kubernetes/manifests/    # K8s deployments, services, HPA, ingress
│   ├── terraform/
│   │   ├── aws/                 # VPC, EKS, RDS, S3, EC2, ElastiCache
│   │   └── azure/               # AKS, ACR, PostgreSQL, Redis, Storage
│   ├── monitoring/
│   │   ├── grafana/dashboards/  # Grafana dashboard configs
│   │   ├── elk/                 # Logstash pipeline, ES index templates
│   │   └── datadog/             # Datadog agent config
│   ├── jenkins/                 # Jenkinsfile for CI/CD pipeline
│   ├── sonarqube/               # SonarQube project config
│   ├── security/                # Veracode scan config
│   └── messaging/               # Kafka topic creation scripts
├── aws_lambda/                  # Lambda function for serverless event processing
├── tests/
│   ├── unit/                    # Unit tests for Django, FastAPI, Flask
│   └── integration/             # End-to-end API integration tests
├── .github/workflows/           # GitHub Actions CI/CD pipelines
├── docker-compose.yml           # Full local development stack
├── .env.example                 # Environment variable template
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/datapulse-analytics.git
cd datapulse-analytics
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services with Docker Compose**
```bash
docker-compose up -d
```

4. **Run database migrations**
```bash
docker exec datapulse-django python manage.py migrate
docker exec datapulse-django python manage.py createsuperuser
```

5. **Access the applications**
- React Dashboard: http://localhost:3000
- Angular Admin: http://localhost:4200
- Django API: http://localhost:8000/swagger/
- FastAPI Docs: http://localhost:8001/docs
- Flask AI Service: http://localhost:5001/api/v1/health
- Grafana: http://localhost:3001
- Kibana: http://localhost:5601
- RabbitMQ Management: http://localhost:15672

### Running Without Docker

**Django API:**
```bash
cd backend/django_app
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**FastAPI Ingestion Service:**
```bash
cd backend/fastapi_service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Flask AI Service:**
```bash
cd backend/flask_ai_service
pip install -r requirements.txt
python wsgi.py
```

**React Dashboard:**
```bash
cd frontend/react-dashboard
npm install
npm start
```

**Angular Admin:**
```bash
cd frontend/angular-admin
npm install
npm start
```

## API Endpoints

### Django API (Port 8000)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register/` | User registration |
| POST | `/api/v1/users/login/` | JWT authentication |
| GET | `/api/v1/users/profile/` | User profile |
| GET | `/api/v1/analytics/dashboards/` | List dashboards |
| POST | `/api/v1/analytics/sources/` | Create data source |
| GET | `/api/v1/analytics/events/` | List events |
| POST | `/api/v1/analytics/events/bulk_ingest/` | Bulk event ingestion |
| GET | `/api/v1/analytics/alerts/` | List alerts |
| POST | `/api/v1/analytics/reports/` | Generate report |
| GET | `/api/v1/health/live/` | Health check |

### FastAPI Ingestion (Port 8001)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ingest/event` | Ingest single event |
| POST | `/api/v1/ingest/bulk` | Bulk event ingestion |
| POST | `/api/v1/ingest/webhook/{source_id}` | Webhook ingestion |
| POST | `/api/v1/search/query` | Search events |
| GET | `/api/v1/search/aggregate` | Aggregate analytics |
| WS | `/ws/events/{channel}` | Real-time event stream |

### Flask AI Service (Port 5001)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/summarize` | AI-powered data summarization |
| POST | `/api/v1/ai/analyze` | Trend/anomaly analysis |
| POST | `/api/v1/ai/nl-query` | Natural language to ES query |
| POST | `/api/v1/ai/anomaly-detect` | Statistical anomaly detection |
| POST | `/api/v1/ai/report-summary` | AI report generation |

## Infrastructure

### Kubernetes Deployment
```bash
kubectl apply -f infrastructure/kubernetes/manifests/namespace-config.yaml
kubectl apply -f infrastructure/kubernetes/manifests/
```

### Terraform (AWS)
```bash
cd infrastructure/terraform/aws
terraform init
terraform plan -var="db_password=your-secure-password"
terraform apply
```

### Terraform (Azure)
```bash
cd infrastructure/terraform/azure
terraform init
terraform plan -var="db_password=your-secure-password"
terraform apply
```

## CI/CD Pipeline

The project uses both **GitHub Actions** and **Jenkins** for CI/CD:

1. **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push/PR
   - Python linting (flake8, black)
   - Django, FastAPI, Flask unit tests
   - React and Angular builds
   - SonarQube code quality analysis
   - Docker image builds

2. **CD Pipeline** (`.github/workflows/cd.yml`): Runs on main branch pushes
   - Builds and pushes Docker images to ECR
   - Deploys to staging (auto)
   - Deploys to production (on tags, with approval)

3. **Jenkins Pipeline** (`infrastructure/jenkins/Jenkinsfile`): Alternative CI/CD
   - Parallel test execution
   - SonarQube and Veracode scans
   - Docker build and push
   - Kubernetes deployment

## Monitoring & Observability

- **Grafana**: Custom dashboards for event rates, API latency, error rates, Kafka lag
- **ELK Stack**: Centralized logging with Logstash pipelines and Kibana visualizations
- **Datadog**: Infrastructure monitoring, APM, and log aggregation
- **Health Endpoints**: `/health/live/` and `/health/ready/` on all services

## Testing

```bash
# Django unit tests
cd backend/django_app && python manage.py test

# FastAPI tests
cd backend/fastapi_service && pytest tests/ -v

# Flask AI tests
cd backend/flask_ai_service && pytest tests/ -v

# Integration tests (requires running services)
pytest tests/integration/ -v
```

## Security

- JWT-based authentication with token rotation
- CORS configuration per environment
- Rate limiting on all API endpoints
- Veracode static analysis scanning
- SonarQube code quality gates
- AWS S3 server-side encryption (AES-256)
- Kubernetes secrets for sensitive configuration
- Terraform state encryption

## License

MIT License - see [LICENSE](LICENSE) for details.
