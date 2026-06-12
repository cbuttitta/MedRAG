# MedRAG
 
A RAG-powered clinical decision support API that accepts freeform patient biomarker data and visit notes, retrieves semantically relevant medical literature, and returns structured, source-attributed treatment recommendations.
 
---
 
## What it does
 
Paste in a patient's lab values and visit notes. MedRAG infers the relevant conditions, searches a curated database of medical guidelines for supporting evidence, and returns a structured set of actionable recommendations — each one grounded in a real source.
 
```
Patient: 54-year-old male. HbA1c 7.9%, LDL 142 mg/dL, fasting glucose 168.
Visit notes: fatigue, increased thirst. No current medications.
```
 
Returns:
 
```json
{
  "inferred_conditions": ["Type 2 Diabetes", "Hyperlipidemia"],
  "recommendations": [
    {
      "category": "Diet",
      "action": "Reduce carbohydrate intake to below 130g per day, emphasizing low-glycemic foods such as legumes, non-starchy vegetables, and whole grains.",
      "rationale": "HbA1c of 7.9% indicates suboptimal glycemic control. Carbohydrate reduction is the most evidence-supported first-line dietary intervention.",
      "sources": ["ADA Standards of Care 2026 — Nutrition Therapy"]
    }
  ],
  "disclaimer": "These recommendations are for informational purposes only..."
}
```
 
---
 
## How it works
 
MedRAG uses **Retrieval-Augmented Generation (RAG)** — rather than relying on the language model's training data alone, it first retrieves relevant passages from a trusted medical literature database, then grounds the model's output in that evidence.
 
```
Patient input
     │
     ▼
Condition extraction (GPT-4o-mini)
     │
     ▼
Vector similarity search (pgvector)
     │
     ▼
Augmented prompt with retrieved context
     │
     ▼
Structured recommendation generation (GPT-4o-mini)
     │
     ▼
Validated JSON response
```
 
Every recommendation includes source attribution — if the model can't ground a recommendation in the retrieved literature, it doesn't make it.
 
---
 
## Tech stack
 
| Layer | Technology |
|---|---|
| API | Python, Flask, Pydantic |
| LLM & Embeddings | OpenAI GPT-4o-mini, text-embedding-3-small |
| Vector Search | PostgreSQL + pgvector |
| Frontend | React, Vite |
| Containerization | Docker, Docker Compose |
| Cloud | AWS ECS Fargate, RDS PostgreSQL, ECR |
| CI/CD | GitHub Actions |
| Auth | API key header (`X-API-Key`) |
 
---
 
## Document corpus
 
Recommendations are grounded in manually curated chunks from the following sources:
 
- **ADA Standards of Care 2026** — nutrition therapy, physical activity
- **NIH MedlinePlus** — diabetes, high cholesterol, hypertension, hypothyroidism, obesity
- **Physical Activity Guidelines for Americans, 2nd Edition** (HHS/ODPHP)
---
 
## API reference
 
### `POST /api/recommend`
 
**Headers**
```
X-API-Key: your-api-key
Content-Type: application/json
```
 
**Request body**
```json
{
  "raw_text": "Freeform patient data — lab values and visit notes as plain text"
}
```
 
**Response**
```json
{
  "inferred_conditions": ["string"],
  "recommendations": [
    {
      "category": "Diet | Exercise | Lifestyle | Supplement",
      "action": "string",
      "rationale": "string",
      "sources": ["string"]
    }
  ],
  "disclaimer": "string"
}
```
 
**Error responses**
 
| Status | Meaning |
|---|---|
| `401` | Missing or invalid API key |
| `422` | Empty or invalid request body |
| `500` | LLM or database error |
 
### `GET /health`
 
Returns `{"status": "ok"}`. No API key required. Used by ECS health checks.
 
---
 
## Running locally
 
**Prerequisites:** Docker Desktop, an OpenAI API key.
 
**1. Clone and configure**
```bash
git clone https://github.com/cbuttitta/medrag.git
cd medrag
cp .env.example .env
# Fill in OPENAI_API_KEY and MEDRAG_API_KEY in .env
```
 
**2. Start the stack**
```bash
docker compose up --build
```
 
This starts three containers: PostgreSQL with pgvector, the Flask API, and the React frontend.
 
**3. Run the database migration**
```bash
docker exec -i medrag-postgres psql -U postgres -d medrag < api/db/migrations/001_init.sql
```
 
**4. Ingest the medical literature corpus**
```bash
docker exec -it medrag-postgres bash -c "
  apt-get update -q && apt-get install -y -q python3 python3-pip &&
  pip3 install openai psycopg2-binary python-dotenv --break-system-packages -q &&
  DATABASE_URL='postgresql://postgres:password@localhost:5432/medrag' \
  OPENAI_API_KEY='your-key-here' \
  python3 /ingest.py
"
```
 
**5. Open the app**
 
Visit `http://localhost:5173` — the form is prefilled with a sample patient input so you can demo immediately.
 
To call the API directly:
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "X-API-Key: your-medrag-api-key" \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "HbA1c 7.9%, LDL 142, fasting glucose 168. Patient reports fatigue."}'
```
 
---
 
## Project structure
 
```
medrag/
├── api/
│   ├── app.py                   # Flask app factory, auth middleware
│   ├── routes/
│   │   └── recommend.py         # POST /api/recommend
│   ├── services/
│   │   ├── extractor.py         # LLM: extract conditions from input
│   │   ├── retriever.py         # pgvector similarity search
│   │   └── recommender.py       # LLM: generate structured recommendations
│   ├── models/
│   │   └── schemas.py           # Pydantic input/output validation
│   └── db/
│       └── migrations/
│           └── 001_init.sql     # pgvector setup, table definitions
├── scripts/
│   ├── ingest.py                # One-time corpus ingestion script
│   └── corpus/                  # Curated medical literature text files
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── PatientForm.jsx
│       │   └── RecommendationCard.jsx
│       └── App.jsx
├── Dockerfile.api
├── Dockerfile.frontend
├── docker-compose.yml
└── .github/
    └── workflows/
        └── deploy.yml           # GitHub Actions CI/CD
```
 
---
 
## Deployment
 
The project deploys to AWS ECS Fargate with RDS PostgreSQL. On every push to `main`, GitHub Actions builds both Docker images, pushes them to ECR, and forces a new ECS deployment.
 
Infrastructure:
- **ECS Fargate** — runs API and frontend containers, no server management
- **RDS PostgreSQL 16** — managed database with pgvector extension enabled
- **ECR** — private Docker image registry
- **ALB** — Application Load Balancer routing traffic to both services
- **Secrets Manager** — stores `OPENAI_API_KEY`, `MEDRAG_API_KEY`, and `DATABASE_URL`
---
 
## Disclaimer
 
MedRAG is a portfolio project demonstrating RAG architecture applied to clinical data. It is not a medical device and should not be used to make real clinical decisions. All recommendations are for informational and educational purposes only. Always consult a qualified healthcare provider.
 
---
 
## Author
 
Case Buttitta · [LinkedIn](https://linkedin.com/in/case-buttitta) · [GitHub](https://github.com/cbuttitta)
