"""
Comprehensive skill dictionaries for Kenya Tech Landscape analysis.
Used for regex-based skill extraction from job descriptions.
"""

# Skill variants for normalization (raw -> canonical)
SKILL_VARIANTS = {
    # Power BI variants
    "PowerBI": "Power BI",
    "powerbi": "Power BI",
    "MS Power BI": "Power BI",
    
    # PostgreSQL variants
    "Postgres": "PostgreSQL",
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    
    # JavaScript variants
    "Javascript": "JavaScript",
    "JS": "JavaScript",
    "javascript": "JavaScript",
    
    # TypeScript variants
    "Typescript": "TypeScript",
    "TS": "TypeScript",
    
    # Node.js variants
    "NodeJS": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    
    # Vue.js variants
    "VueJS": "Vue.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    
    # React variants
    "ReactJS": "React",
    "react.js": "React",
    
    # scikit-learn variants
    "sklearn": "scikit-learn",
    "Scikit-learn": "scikit-learn",
    "Sklearn": "scikit-learn",
    
    # TensorFlow variants
    "Tensorflow": "TensorFlow",
    "tensorflow": "TensorFlow",
    
    # PyTorch variants
    "Pytorch": "PyTorch",
    "pytorch": "PyTorch",
    
    # MongoDB variants
    "Mongo": "MongoDB",
    "mongo": "MongoDB",
    
    # MySQL variants
    "mysql": "MySQL",
    "MYSQL": "MySQL",
    
    # CI/CD variants
    "cicd": "CI/CD",
    "CICD": "CI/CD",
    "ci cd": "CI/CD",
}

# ============================================================
# DATA SCIENCE / ANALYTICS SKILLS
# ============================================================
DATA_SCIENCE_SKILLS = {
    "languages": [
        "Python", "R", "SQL", "Julia", "Scala", "SAS", "MATLAB", "Java"
    ],
    
    "ml_ai_frameworks": [
        # Deep Learning
        "TensorFlow", "PyTorch", "Keras", "JAX", "MXNet",
        # ML Libraries
        "scikit-learn", "XGBoost", "LightGBM", "CatBoost",
        # AutoML
        "H2O", "Auto-sklearn", "TPOT",
        # NLP
        "Hugging Face", "spaCy", "NLTK", "Gensim", "Transformers",
        # GenAI
        "LangChain", "LlamaIndex", "OpenAI API", "Langsmith",
        # Computer Vision
        "OpenCV", "YOLO", "Detectron",
    ],
    
    "data_processing": [
        "Pandas", "NumPy", "Polars", "Dask", "PySpark",
        "Vaex", "Modin", "cuDF",
    ],
    
    "visualization": [
        "Matplotlib", "Seaborn", "Plotly", "Altair", "D3.js",
        "Bokeh", "ggplot2", "Dash",
    ],
    
    "bi_tools": [
        "Tableau", "Power BI", "Looker", "Metabase", "Superset",
        "Qlik", "QlikView", "Sisense", "Domo", "ThoughtSpot",
        "Google Data Studio", "SSRS", "SSIS", "SSAS",
    ],
    
    "big_data": [
        "Spark", "Hadoop", "Hive", "Kafka", "Flink", "Airflow",
        "Presto", "Trino", "Beam", "Storm", "Pig", "Sqoop",
        "HDFS", "MapReduce", "Zookeeper",
    ],
    
    "databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "Snowflake", "BigQuery", "Redshift", "Databricks",
        "ClickHouse", "Cassandra", "HBase", "Neo4j", "DynamoDB",
        "Oracle", "SQL Server", "MariaDB", "CouchDB", "InfluxDB",
    ],
    
    "mlops": [
        "MLflow", "Kubeflow", "DVC", "Weights & Biases", "SageMaker",
        "Vertex AI", "Azure ML", "BentoML", "Seldon", "Feast",
        "Great Expectations", "Evidently", "WhyLabs",
    ],
    
    "concepts": [
        "machine learning", "deep learning", "NLP", "natural language processing",
        "computer vision", "neural network", "regression", "classification",
        "clustering", "time series", "feature engineering", "A/B testing",
        "statistical analysis", "predictive modeling", "data mining",
        "ETL", "data pipeline", "data warehouse", "data lake",
        "anomaly detection", "recommendation system", "sentiment analysis",
        "reinforcement learning", "generative AI", "LLM",
    ],
}

# ============================================================
# WEB DEVELOPMENT SKILLS
# ============================================================
WEB_DEV_SKILLS = {
    "languages": [
        "JavaScript", "TypeScript", "Python", "PHP", "Ruby", "Go",
        "Rust", "Java", "C#", "Kotlin", "Swift", "Dart",
    ],
    
    "frontend_frameworks": [
        "React", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js",
        "Remix", "Astro", "SolidJS", "Qwik", "Gatsby", "Ember",
        "jQuery", "Backbone", "Alpine.js", "HTMX", "Lit",
    ],
    
    "css_styling": [
        "Tailwind CSS", "Bootstrap", "Sass", "SCSS", "Less",
        "CSS-in-JS", "styled-components", "Emotion", "Material UI",
        "Chakra UI", "Ant Design", "Shadcn", "Radix UI",
        "Bulma", "Foundation", "Semantic UI",
    ],
    
    "backend_frameworks": [
        "Node.js", "Express", "NestJS", "Fastify", "Koa",
        "Django", "Flask", "FastAPI", "Pyramid",
        "Ruby on Rails", "Sinatra",
        "Laravel", "Symfony", "CodeIgniter",
        "Spring Boot", "Spring", "Micronaut", "Quarkus",
        "ASP.NET", ".NET Core", "Blazor",
        "Gin", "Echo", "Fiber",
    ],
    
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite",
        "Prisma", "Sequelize", "TypeORM", "Mongoose", "Drizzle",
        "Knex", "SQLAlchemy", "ActiveRecord",
    ],
    
    "devops_tools": [
        "Docker", "Kubernetes", "AWS", "Azure", "GCP",
        "Vercel", "Netlify", "Heroku", "DigitalOcean", "Linode",
        "Nginx", "Apache", "Caddy",
        "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins", "CircleCI",
        "Terraform", "Ansible", "Puppet", "Chef",
        "Prometheus", "Grafana", "Datadog", "New Relic",
    ],
    
    "testing": [
        "Jest", "Cypress", "Playwright", "Vitest", "Mocha", "Chai",
        "pytest", "unittest", "RSpec", "Jasmine", "Karma",
        "Selenium", "Puppeteer", "Testing Library",
    ],
    
    "api_tools": [
        "REST", "RESTful", "GraphQL", "gRPC", "WebSocket",
        "Swagger", "OpenAPI", "Postman", "Insomnia",
        "Apollo", "Hasura", "tRPC",
    ],
    
    "mobile": [
        "React Native", "Flutter", "Ionic", "Xamarin",
        "Swift", "Kotlin", "SwiftUI", "Jetpack Compose",
    ],
}

# ============================================================
# CYBER SECURITY SKILLS
# ============================================================
CYBER_SECURITY_SKILLS = {
    "concepts": [
        "penetration testing", "vulnerability assessment", "SIEM",
        "incident response", "threat intelligence", "SOC",
        "encryption", "firewall", "IDS", "IPS",
        "network security", "application security", "cloud security",
        "identity management", "access control", "IAM",
        "risk assessment", "compliance", "audit",
        "malware analysis", "reverse engineering", "forensics",
        "red team", "blue team", "purple team",
        "OWASP", "zero trust", "security architecture",
    ],
    
    "tools": [
        "Wireshark", "Metasploit", "Nmap", "Burp Suite", "Nessus",
        "Splunk", "CrowdStrike", "Palo Alto", "Fortinet",
        "Qualys", "Tenable", "Rapid7", "Carbon Black",
        "Snort", "Suricata", "OSSEC", "Wazuh",
        "Kali Linux", "Parrot OS", "Hashcat", "John the Ripper",
        "Cobalt Strike", "BloodHound", "Mimikatz",
        "Shodan", "theHarvester", "Maltego",
    ],
    
    "certifications": [
        "CISSP", "CEH", "OSCP", "CompTIA Security+", "ISO 27001",
        "CISM", "CISA", "GIAC", "CCSP", "CRISC",
        "GCIH", "GPEN", "GWAPT", "GSEC",
        "AWS Security", "Azure Security", "GCP Security",
    ],
    
    "frameworks": [
        "NIST", "CIS Controls", "MITRE ATT&CK", "STRIDE",
        "PCI DSS", "HIPAA", "GDPR", "SOC 2", "SOX",
    ],
}

# ============================================================
# SOFT SKILLS
# ============================================================
SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "adaptability", "collaboration",
    "time management", "attention to detail", "presentation",
    "analytical", "interpersonal", "organization", "proactive",
    "self-motivated", "creativity", "negotiation", "mentoring",
    "decision making", "conflict resolution", "stakeholder management",
    "agile", "scrum", "project management",
]

# ============================================================
# DOMAIN CLASSIFICATION KEYWORDS
# ============================================================
DOMAIN_KEYWORDS = {
    "data_science": [
        "data scientist", "data analyst", "machine learning", "ml engineer",
        "data engineer", "bi ", "business intelligence", "analytics",
        "statistician", "research scientist", "ai engineer", "nlp",
        "computer vision", "deep learning", "quantitative",
    ],
    "web_dev": [
        "developer", "software engineer", "frontend", "backend",
        "full stack", "fullstack", "web", "devops", "sre",
        "mobile developer", "ios developer", "android developer",
        "react developer", "node developer", "python developer",
    ],
    "cyber_security": [
        "security", "cyber", "infosec", "soc analyst", "penetration",
        "vulnerability", "security engineer", "ciso", "iam",
        "threat", "incident response", "forensic",
    ],
}

# Flatten all skills for easy lookup
def get_all_skills():
    """Return a flat list of all technical skills with their domains."""
    skills = []
    
    for category, skill_list in DATA_SCIENCE_SKILLS.items():
        for skill in skill_list:
            skills.append({"skill": skill, "domain": "data_science", "category": category})
    
    for category, skill_list in WEB_DEV_SKILLS.items():
        for skill in skill_list:
            skills.append({"skill": skill, "domain": "web_dev", "category": category})
    
    for category, skill_list in CYBER_SECURITY_SKILLS.items():
        for skill in skill_list:
            skills.append({"skill": skill, "domain": "cyber_security", "category": category})
    
    for skill in SOFT_SKILLS:
        skills.append({"skill": skill, "domain": "general", "category": "soft_skills"})
    
    return skills


def get_skill_lookup():
    """Return a dictionary mapping lowercase skill names to canonical form."""
    lookup = {}
    for skill_info in get_all_skills():
        skill = skill_info["skill"]
        lookup[skill.lower()] = skill
    
    # Add variants
    for variant, canonical in SKILL_VARIANTS.items():
        lookup[variant.lower()] = canonical
    
    return lookup
