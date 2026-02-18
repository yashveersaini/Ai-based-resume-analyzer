import joblib
import numpy as np
import os

# ── Load trained model files (once at startup) ──
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR  = os.path.join(BASE_DIR, 'models')

tfidf   = joblib.load(os.path.join(MODEL_DIR, 'tfidf.pkl'))
clf     = joblib.load(os.path.join(MODEL_DIR, 'job_model.pkl'))
le      = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))


# ── Job Role Profiles ──
JOB_PROFILES = {

    "Data Scientist": {
        "skills": [
            "python", "machine learning", "deep learning", "tensorflow", "pytorch",
            "scikit-learn", "pandas", "numpy", "statistics", "data analysis",
            "nlp", "sql", "data visualization", "matplotlib", "seaborn",
            "feature engineering", "model deployment", "jupyter", "r",
        ],
        "roadmap": [
            {"step": 1, "title": "Programming Foundation",     "desc": "Master Python (NumPy, Pandas, Matplotlib). Learn R basics."},
            {"step": 2, "title": "Mathematics & Statistics",   "desc": "Linear algebra, probability, statistics, hypothesis testing, A/B testing."},
            {"step": 3, "title": "Machine Learning",           "desc": "Supervised & unsupervised learning with scikit-learn. Master regression, classification, clustering."},
            {"step": 4, "title": "Deep Learning",              "desc": "Neural networks, CNNs, RNNs with TensorFlow/PyTorch. Study Transformers."},
            {"step": 5, "title": "NLP & Computer Vision",      "desc": "Text processing with spaCy/NLTK, BERT fine-tuning, image classification."},
            {"step": 6, "title": "Data Engineering",           "desc": "SQL, ETL pipelines, cloud storage (AWS S3, BigQuery). Learn dbt."},
            {"step": 7, "title": "Model Deployment",           "desc": "REST APIs with FastAPI/Flask, Docker containers, MLflow experiment tracking."},
            {"step": 8, "title": "Portfolio & Kaggle",         "desc": "Build 3–5 end-to-end projects. Compete on Kaggle. Publish on GitHub."},
        ]
    },

    "Web Developer": {
        "skills": [
            "html", "css", "javascript", "typescript", "react", "angular", "vue",
            "node.js", "express", "rest api", "mongodb", "postgresql", "mysql",
            "git", "docker", "graphql", "tailwind", "next.js", "webpack", "npm",
        ],
        "roadmap": [
            {"step": 1, "title": "HTML & CSS Fundamentals",    "desc": "Semantic HTML5, CSS3, Flexbox, Grid, responsive design, accessibility."},
            {"step": 2, "title": "JavaScript Mastery",         "desc": "ES6+, DOM, async/await, fetch API, modules, TypeScript basics."},
            {"step": 3, "title": "Frontend Framework",         "desc": "Pick React or Vue or Angular. Learn state management (Redux/Pinia/NgRx)."},
            {"step": 4, "title": "Backend Development",        "desc": "Node.js + Express, RESTful APIs, authentication (JWT, OAuth)."},
            {"step": 5, "title": "Databases",                  "desc": "SQL (PostgreSQL/MySQL) and NoSQL (MongoDB). Learn ORM (Prisma/Sequelize)."},
            {"step": 6, "title": "DevOps Basics",              "desc": "Git/GitHub, CI/CD pipelines, Docker basics, Vercel/Netlify deployment."},
            {"step": 7, "title": "Performance & Security",     "desc": "Web vitals, lazy loading, HTTPS, CORS, XSS/CSRF prevention, CSP headers."},
            {"step": 8, "title": "Build Projects",             "desc": "Ship 3 full-stack projects. Contribute to open source. Build your portfolio site."},
        ]
    },

    "DevOps Engineer": {
        "skills": [
            "docker", "kubernetes", "jenkins", "aws", "azure", "gcp", "terraform",
            "ansible", "linux", "bash", "git", "ci/cd", "helm", "prometheus",
            "grafana", "monitoring", "github actions", "gitlab", "python",
        ],
        "roadmap": [
            {"step": 1, "title": "Linux & Scripting",          "desc": "Linux administration, bash scripting, cron jobs, file systems, networking."},
            {"step": 2, "title": "Version Control & CI/CD",    "desc": "Git mastery, GitHub Actions, GitLab CI, Jenkins pipelines."},
            {"step": 3, "title": "Containers",                 "desc": "Docker (build, run, compose). Understand container registries and security."},
            {"step": 4, "title": "Container Orchestration",    "desc": "Kubernetes (pods, services, deployments, Helm charts, namespaces)."},
            {"step": 5, "title": "Infrastructure as Code",     "desc": "Terraform for provisioning, Ansible for configuration management."},
            {"step": 6, "title": "Cloud Platforms",            "desc": "AWS (EC2, S3, EKS, RDS, IAM) or Azure/GCP equivalents. Get certified."},
            {"step": 7, "title": "Monitoring & Observability", "desc": "Prometheus, Grafana, ELK stack, alerting, log aggregation, tracing."},
            {"step": 8, "title": "Security & Compliance",      "desc": "DevSecOps, secret management (Vault), SAST/DAST, network security."},
        ]
    },

    "Data Analyst": {
        "skills": [
            "sql", "excel", "power bi", "tableau", "python", "pandas",
            "data visualization", "statistics", "reporting", "communication",
            "google analytics", "looker", "dax", "etl", "data cleaning",
        ],
        "roadmap": [
            {"step": 1, "title": "Excel Mastery",              "desc": "VLOOKUP, pivot tables, power query, charts. Excel is the foundation."},
            {"step": 2, "title": "SQL",                        "desc": "SELECT, JOINs, GROUP BY, subqueries, window functions, CTEs."},
            {"step": 3, "title": "Data Visualization",         "desc": "Tableau or Power BI (DAX). Design dashboards that tell a story."},
            {"step": 4, "title": "Python for Analytics",       "desc": "Pandas for data wrangling, Matplotlib/Seaborn for charts, Jupyter notebooks."},
            {"step": 5, "title": "Statistics",                 "desc": "Descriptive stats, distributions, hypothesis testing, regression basics."},
            {"step": 6, "title": "Business Acumen",            "desc": "KPIs, cohort analysis, funnel analysis, A/B testing, storytelling with data."},
            {"step": 7, "title": "Cloud & Big Data Basics",    "desc": "BigQuery, Snowflake, AWS Redshift basics. Learn dbt for transformations."},
            {"step": 8, "title": "Communication & Portfolio",  "desc": "Present analysis clearly. Build a portfolio with real business insights."},
        ]
    },

    "Backend Developer": {
        "skills": [
            "python", "java", "node.js", "go", "django", "flask", "fastapi",
            "spring boot", "rest api", "postgresql", "mysql", "redis",
            "mongodb", "docker", "git", "linux", "microservices", "kafka",
        ],
        "roadmap": [
            {"step": 1, "title": "Programming Language",       "desc": "Deep-dive: Python (Django/FastAPI), Java (Spring Boot), or Node.js (Express)."},
            {"step": 2, "title": "Databases",                  "desc": "SQL (PostgreSQL, MySQL) + NoSQL (MongoDB, Redis). Master query optimization."},
            {"step": 3, "title": "API Design",                 "desc": "REST APIs (versioning, pagination, auth). GraphQL basics. OpenAPI/Swagger docs."},
            {"step": 4, "title": "Authentication & Security",  "desc": "JWT, OAuth2, session management, rate limiting, input validation."},
            {"step": 5, "title": "Caching & Messaging",        "desc": "Redis caching, Celery tasks, message queues (RabbitMQ/Kafka)."},
            {"step": 6, "title": "Containerization",           "desc": "Docker, docker-compose. Understand multi-stage builds and secrets."},
            {"step": 7, "title": "System Design",              "desc": "Scalability, load balancing, microservices architecture, distributed systems."},
            {"step": 8, "title": "Production Skills",          "desc": "CI/CD, logging, monitoring, cloud deployment (AWS/GCP). Code reviews."},
        ]
    },

    "Mobile Developer": {
        "skills": [
            "android", "ios", "kotlin", "swift", "java", "react native",
            "flutter", "dart", "firebase", "rest api", "git", "mvvm",
            "jetpack compose", "swiftui", "xcode", "room",
        ],
        "roadmap": [
            {"step": 1, "title": "Choose Your Platform",       "desc": "Android (Kotlin + Jetpack Compose) or iOS (Swift + SwiftUI) or cross-platform (Flutter/React Native)."},
            {"step": 2, "title": "UI Development",             "desc": "Layouts, navigation, lists, animations. Follow platform design guidelines (Material/HIG)."},
            {"step": 3, "title": "State Management",           "desc": "MVVM, BLoC, Redux, Provider. Understand reactive programming."},
            {"step": 4, "title": "Networking",                 "desc": "REST APIs with Retrofit/Alamofire/Axios. JSON parsing. Error handling."},
            {"step": 5, "title": "Local Storage",              "desc": "Room (Android), Core Data (iOS), SQLite, SharedPreferences/UserDefaults."},
            {"step": 6, "title": "Firebase & Backend",         "desc": "Firebase Auth, Firestore, FCM push notifications, Analytics."},
            {"step": 7, "title": "Testing & Publishing",       "desc": "Unit tests, UI tests. Publish to Play Store & App Store. CI/CD with Fastlane."},
            {"step": 8, "title": "Advanced Topics",            "desc": "Offline-first architecture, performance optimization, accessibility, deep links."},
        ]
    },

    "Cybersecurity Analyst": {
        "skills": [
            "penetration testing", "python", "linux", "network security", "kali",
            "burp suite", "metasploit", "siem", "splunk", "wireshark", "nmap",
            "owasp", "incident response", "vulnerability assessment", "ethical hacking",
        ],
        "roadmap": [
            {"step": 1, "title": "Networking Fundamentals",    "desc": "TCP/IP, DNS, HTTP, firewalls, VPNs. Use Wireshark to analyze traffic."},
            {"step": 2, "title": "Linux Mastery",              "desc": "Linux command line, file permissions, processes, Bash scripting. Use Kali Linux."},
            {"step": 3, "title": "Ethical Hacking Basics",     "desc": "OWASP Top 10, Nmap, Metasploit, Burp Suite. Practice on HackTheBox/TryHackMe."},
            {"step": 4, "title": "Security Operations",        "desc": "SOC workflows, SIEM (Splunk/QRadar), log analysis, alert triage."},
            {"step": 5, "title": "Penetration Testing",        "desc": "Web app, network, and mobile pentesting. Reporting vulnerabilities professionally."},
            {"step": 6, "title": "Incident Response",          "desc": "Digital forensics, memory analysis, malware triage, IR playbooks."},
            {"step": 7, "title": "Cloud Security",             "desc": "AWS/Azure IAM, zero trust, CSPM tools. Understand cloud threat models."},
            {"step": 8, "title": "Certifications",             "desc": "Pursue CompTIA Security+, CEH, OSCP, CISSP. Build a home lab."},
        ]
    },

    "Cloud Engineer": {
        "skills": [
            "aws", "azure", "gcp", "terraform", "kubernetes", "docker",
            "python", "linux", "git", "lambda", "s3", "ec2", "rds",
            "cloudwatch", "iam", "networking", "ci/cd",
        ],
        "roadmap": [
            {"step": 1, "title": "Cloud Fundamentals",         "desc": "Understand IaaS/PaaS/SaaS. Pick AWS or Azure or GCP. Get free tier account."},
            {"step": 2, "title": "Core Services",              "desc": "Compute (EC2/VMs), Storage (S3/Blob), Networking (VPC/VNet), IAM/RBAC."},
            {"step": 3, "title": "Infrastructure as Code",     "desc": "Terraform for multi-cloud provisioning. Learn modules and state management."},
            {"step": 4, "title": "Containers & Orchestration", "desc": "Docker + Kubernetes (EKS/AKS/GKE). Helm charts, namespaces, autoscaling."},
            {"step": 5, "title": "Serverless",                 "desc": "AWS Lambda, Azure Functions, Cloud Run. Event-driven architectures."},
            {"step": 6, "title": "Networking & Security",      "desc": "VPCs, subnets, security groups, WAF, load balancers, CDN, DNS."},
            {"step": 7, "title": "Monitoring & Cost",          "desc": "CloudWatch/Azure Monitor, cost optimization (Reserved Instances, spot), FinOps."},
            {"step": 8, "title": "Certifications",             "desc": "AWS Solutions Architect / Azure Administrator / GCP ACE. Then specializations."},
        ]
    },

    "ML Engineer": {
        "skills": [
            "python", "mlops", "docker", "kubernetes", "mlflow", "airflow",
            "tensorflow", "pytorch", "scikit-learn", "git", "aws", "sagemaker",
            "model deployment", "rest api", "feature engineering", "spark",
        ],
        "roadmap": [
            {"step": 1, "title": "ML Foundations",             "desc": "Python, scikit-learn, pandas, statistics, model evaluation. Understand the full ML lifecycle."},
            {"step": 2, "title": "Deep Learning",              "desc": "TensorFlow or PyTorch. CNNs, RNNs, Transformers, fine-tuning pre-trained models."},
            {"step": 3, "title": "Data Pipelines",             "desc": "Apache Airflow, Spark/PySpark, feature stores (Feast). ETL at scale."},
            {"step": 4, "title": "Model Serving",              "desc": "REST APIs (FastAPI/Flask), TF Serving, Triton Inference Server, ONNX."},
            {"step": 5, "title": "MLOps Tooling",              "desc": "MLflow (tracking, registry), DVC, Weights & Biases, experiment management."},
            {"step": 6, "title": "Containerization & Orchestration", "desc": "Docker, Kubernetes, Kubeflow. Scalable model training and deployment."},
            {"step": 7, "title": "Cloud ML Platforms",         "desc": "AWS SageMaker, GCP Vertex AI, Azure ML. Managed training and deployment."},
            {"step": 8, "title": "LLMs & Advanced Topics",     "desc": "Fine-tuning LLMs, RAG pipelines, vector databases, prompt engineering."},
        ]
    },

    "Database Administrator": {
        "skills": [
            "sql", "postgresql", "mysql", "oracle", "sql server", "mongodb",
            "redis", "cassandra", "snowflake", "backup", "replication",
            "performance tuning", "linux", "python", "high availability",
        ],
        "roadmap": [
            {"step": 1, "title": "SQL Mastery",                "desc": "Advanced SQL: window functions, CTEs, stored procedures, triggers, indexes."},
            {"step": 2, "title": "Database Internals",         "desc": "Storage engines, query planners, execution plans, ACID properties, transactions."},
            {"step": 3, "title": "Performance Tuning",         "desc": "Index optimization, query rewriting, EXPLAIN ANALYZE, caching, connection pooling."},
            {"step": 4, "title": "Backup & Recovery",          "desc": "Full/incremental backups, point-in-time recovery, RTO/RPO planning, testing restores."},
            {"step": 5, "title": "Replication & HA",           "desc": "Primary-replica setup, failover, load balancing (pgBouncer, ProxySQL)."},
            {"step": 6, "title": "NoSQL Databases",            "desc": "MongoDB, Redis, Cassandra. Understand CAP theorem and when to use NoSQL."},
            {"step": 7, "title": "Cloud Databases",            "desc": "AWS RDS/Aurora, Azure SQL, GCP Cloud SQL, Snowflake, BigQuery."},
            {"step": 8, "title": "Security & Compliance",      "desc": "Encryption at rest/transit, auditing, RBAC, GDPR/HIPAA compliance, data masking."},
        ]
    },
}


def suggest_jobs(resume_skills: list) -> list:
    """
    Given a list of skills extracted from a resume, return the top 3 predicted
    job roles with confidence score, matched skills, and a learning roadmap.

    Args:
        resume_skills: list of skill strings from the resume

    Returns:
        List of up to 3 dicts, each with:
            role, confidence, matched_skills, roadmap
    """
    if not resume_skills:
        return []

    # Join skills into a single string for the TF-IDF vectorizer
    skills_text = ' '.join(resume_skills).lower()
    vec         = tfidf.transform([skills_text])
    proba       = clf.predict_proba(vec)[0]

    # Get top 3 class indices by probability
    top3_idx = np.argsort(proba)[::-1][:3]

    results = []
    resume_set = set(s.lower() for s in resume_skills)

    for idx in top3_idx:
        role       = le.classes_[idx]
        confidence = round(float(proba[idx]) * 100, 1)
        profile    = JOB_PROFILES.get(role, {})

        required_skills = profile.get("skills", [])
        matched_skills  = [s for s in required_skills if s.lower() in resume_set]
        roadmap         = profile.get("roadmap", [])

        results.append({
            "role":           role,
            "confidence":     confidence,
            "matched_skills": matched_skills,
            "total_skills":   len(required_skills),
            "roadmap":        roadmap,
        })

    return results