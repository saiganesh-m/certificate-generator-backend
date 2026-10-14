# Universal Certificate Studio — Backend API 🎓

A production-grade REST API built with **FastAPI**, **SQLAlchemy 2.0**, and **ReportLab** for dynamic certificate generation, universal QR verification, and organizer access control.

---

## 📁 Project Directory Structure

```text
server/
├── .env                              # Environment secrets & configuration (Git-ignored in production)
├── main.py                           # Application entry point, CORS, static storage, & router mounts
├── certificates.db                   # Local SQLite database (auto-created on startup)
├── requirements.txt                  # Python dependencies
│
├── storage/                          # File storage for uploads and runtime assets
│   ├── templates/                    # Uploaded background PDF certificate templates
│   └── outputs/                      # Generated certificate ZIPs and artifacts
│
└── app/
    ├── core/                         # Core infrastructure & system configuration
    │   ├── __init__.py
    │   ├── config.py                 # Centralized settings (Pydantic BaseSettings loading from .env)
    │   └── security.py               # Token hashing & FastAPI 'require_admin' route dependency
    │
    ├── db/                           # Database connection & ORM lifecycle
    │   ├── __init__.py
    │   └── database.py               # SQLAlchemy engine, SessionLocal factory, & get_db dependency
    │
    ├── models/                       # SQLAlchemy Database Tables (ORM layer)
    │   ├── __init__.py
    │   ├── certificate.py            # Certificate table (UUID, event, dates, metadata_json)
    │   └── template.py               # Template table (title, layout_schema, dimensions, file paths)
    │
    ├── schemas/                      # Pydantic Schemas (Data Validation & Serialization)
    │   ├── __init__.py
    │   ├── auth.py                   # VerifyKeyRequest, AuthResponse, AuthStatusResponse
    │   ├── certificate.py            # CertificateVerificationResponse
    │   ├── element.py                # CanvasElement coordinate, font, & typography schema
    │   └── template.py               # TemplateCreate, TemplateResponse
    │
    ├── services/                     # Business Logic & Computational Engines
    │   ├── __init__.py
    │   ├── auth_service.py           # Organizer passkey validation & session issuance
    │   ├── excel_parser.py           # Pandas/OpenPyXL parser, name casing, & acronym preservation
    │   ├── pdf_engine.py             # ReportLab vector overlays, auto-shrink, & in-memory ZIP streamer
    │   └── qr_service.py             # In-memory high-res QR code generator
    │
    └── routers/                      # Thin HTTP Route Controllers (FastAPI endpoints)
        ├── __init__.py
        ├── auth.py                   # /api/v1/auth (passkey verification & status check)
        ├── certificates.py           # /api/v1/certificates (parse data, generate batch, public verify)
        └── templates.py              # /api/v1/templates (CRUD for reusable template layouts)
```

---

## 📑 File & Folder Responsibilities

| File / Folder | Role & Responsibility | Key Dependencies |
| :--- | :--- | :--- |
| `main.py` | Initializes FastAPI, mounts static `/storage`, configures CORS, and registers routers. | `fastapi`, `uvicorn` |
| `.env` | Holds sensitive secrets (`ADMIN_SECRET_KEY`), database URLs, and verification URL templates. | Pydantic Settings |
| `app/core/config.py` | Reads environment variables with defaults; resolves absolute OS-agnostic storage paths. | `pydantic-settings` |
| `app/core/security.py` | Implements cryptographic session token generation and `require_admin` FastAPI dependency. | `hashlib`, `fastapi` |
| `app/db/database.py` | Manages the SQLAlchemy connection pool (`pool_pre_ping=True`) and yield-based `get_db`. | `sqlalchemy` |
| `app/models/` | Defines SQL tables. Uses native `Column(JSON)` for storing arbitrary participant columns. | `sqlalchemy` |
| `app/schemas/` | Validates HTTP payloads and response models; enforces coordinate and font constraints. | `pydantic` |
| `app/services/pdf_engine.py` | Core engine. Overlays text/QRs via ReportLab canvas, merges with base PDF in RAM, streams ZIP. | `reportlab`, `pypdf` |
| `app/services/excel_parser.py`| Parses `.xlsx`, `.xls`, `.csv`. Normalizes title casing while preserving acronyms (`VVL`, `NRI`). | `pandas`, `openpyxl` |
| `app/services/qr_service.py` | Generates high-res PNG byte streams of QR codes in RAM without disk clutter. | `qrcode`, `Pillow` |
| `app/services/auth_service.py`| Validates organizer passkeys against `ADMIN_SECRET_KEY` and returns session tokens. | `app.core.config` |
| `app/routers/` | Thin HTTP controllers that map URL routes to services and enforce authorization. | `fastapi` |

---

## ⚙️ Environment Configuration (`.env.example` & `.env`)

A sample configuration file is provided at [`.env.example`](.env.example). Copy it to create your active `.env`:

```powershell
# Windows PowerShell:
Copy-Item .env.example .env

# Linux / macOS Bash:
cp .env.example .env
```

Contents of `.env.example`:
```env
# Application Branding
PROJECT_NAME="Universal Certificate Studio API"
API_V1_PREFIX="/api/v1"

# Database Connection (SQLite local or MySQL)
DATABASE_URL="sqlite:///./certificates.db"
# DATABASE_URL="mysql+pymysql://root:password123@localhost:3306/certificate_studio?charset=utf8mb4"

# Master Passkey (required by AdminGate to unlock studio)
ADMIN_SECRET_KEY="zap10x-admin-2026"

# Verification URL base embedded into certificate QR codes
VERIFICATION_BASE_URL="http://localhost:5173/verify?id="
```

---

## 🛠️ Step-by-Step Setup & Installation (Standalone Repository)

Follow these steps to set up the backend server from its repository:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/certificate-generator-backend.git
cd certificate-generator-backend
```

### 2. Create and Activate a Python Virtual Environment
- **On Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If execution policies block scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

- **On macOS / Linux (Bash)**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
*(Includes FastAPI, Uvicorn, SQLAlchemy, PyMySQL, Cryptography, ReportLab, PyPDF, Pandas, OpenPyXL, and Pillow).*

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Start the Development Server
```bash
uvicorn main:app --reload --port 8000
```
- Interactive Swagger API Documentation: 👉 `http://localhost:8000/docs`
- Redoc Documentation: 👉 `http://localhost:8000/redoc`
- Server Health Check: 👉 `http://localhost:8000/api/v1/auth/status`

---

## 🐬 How to Set Up & Connect with MySQL

The backend uses **SQLAlchemy 2.0** with the **PyMySQL** driver, allowing seamless switching between SQLite (local dev) and MySQL (production/staging).

### Step 1: Create the MySQL Database
Log into your MySQL console or phpMyAdmin and create a dedicated database with `utf8mb4` encoding (to support any international names or symbols):

```sql
CREATE DATABASE certificate_studio 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

*(Optional: create a dedicated application user)*
```sql
CREATE USER 'cert_admin'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON certificate_studio.* TO 'cert_admin'@'localhost';
FLUSH PRIVILEGES;
```

### Step 2: Update `DATABASE_URL` in `.env`
Edit your `.env` file and replace the SQLite URL with the MySQL connection string:

```env
DATABASE_URL="mysql+pymysql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>?charset=utf8mb4"
```

#### Real-world Examples:
- **Local MySQL on Windows (default root, port 3306)**:
  ```env
  DATABASE_URL="mysql+pymysql://root:password123@localhost:3306/certificate_studio?charset=utf8mb4"
  ```
- **XAMPP / WAMP (default root with no password)**:
  ```env
  DATABASE_URL="mysql+pymysql://root:@localhost:3306/certificate_studio?charset=utf8mb4"
  ```
- **Docker MySQL container**:
  ```env
  DATABASE_URL="mysql+pymysql://app_user:secret@127.0.0.1:3306/certificate_studio?charset=utf8mb4"
  ```
- **Cloud Database (AWS RDS / GCP Cloud SQL / DigitalOcean)**:
  ```env
  DATABASE_URL="mysql+pymysql://dbadmin:ProdSecret2026@mysql-db-instance.rds.amazonaws.com:3306/certificate_studio?charset=utf8mb4"
  ```

### Step 3: Automatic Table Schema Creation
You **do not** need to write manual `CREATE TABLE` scripts!
When FastAPI starts (`uvicorn main:app --reload`), `app/main.py` runs:
```python
Base.metadata.create_all(bind=engine)
```
SQLAlchemy automatically inspects the MySQL database and creates the following tables if they do not already exist:
1. `certificates`: Stores participant UUIDs, names, events, dates, and dynamic JSON metadata.
2. `templates`: Stores reusable layout definitions, page widths, heights, and element JSON schemas.

### Step 4: Connection Pooling & Reliability
Our connection engine in `app/db/database.py` includes built-in enterprise safeguards:
- `pool_pre_ping=True`: Tests whether the MySQL socket is alive before issuing queries; automatically reconnects if dropped.
- `pool_recycle=3600`: Recycles pooled connections every hour, preventing MySQL's default 8-hour `wait_timeout` disconnects (`2006: MySQL server has gone away`).
- `pool_size=10` & `max_overflow=20`: Handles burst traffic during bulk participant certificate generation.

## 🚀 How to Add New Backend Features in the Future

Follow this step-by-step workflow to maintain strict separation of concerns:

### Example: Adding an "Email Certificates" Feature

#### Step 1: Define Schemas (`app/schemas/email.py`)
Create Pydantic input and output models for validation:
```python
from pydantic import BaseModel, EmailStr

class SendCertificateEmailRequest(BaseModel):
    certificate_id: str
    recipient_email: EmailStr
    subject: str = "Your Internship League Certificate"
```

#### Step 2: Define Models if Persistent (`app/models/email_log.py`)
If tracking email delivery history in the database, define an SQLAlchemy model:
```python
from sqlalchemy import Column, String, DateTime
from app.db.database import Base

class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(String(36), primary_key=True)
    recipient = Column(String(255), nullable=False)
    status = Column(String(50), default="sent")
```

#### Step 3: Implement Business Logic (`app/services/email_service.py`)
Put external communication, email formatting, and SMTP logic in a dedicated service:
```python
class EmailService:
    @staticmethod
    async def send_certificate(certificate_id: str, email: str, subject: str):
        # 1. Fetch certificate PDF from DB / storage
        # 2. Attach PDF and dispatch via SMTP / SendGrid / SES
        return {"status": "dispatched"}
```

#### Step 4: Create Thin Router Controller (`app/routers/emails.py`)
Expose the HTTP endpoint and protect it with `require_admin`:
```python
from fastapi import APIRouter, Depends
from app.schemas.email import SendCertificateEmailRequest
from app.services.email_service import EmailService
from app.core.security import require_admin

router = APIRouter(prefix="/emails", tags=["Email Notifications"])

@router.post("/send", dependencies=[Depends(require_admin)])
async def send_email(payload: SendCertificateEmailRequest):
    return await EmailService.send_certificate(
        payload.certificate_id, payload.recipient_email, payload.subject
    )
```

#### Step 5: Mount Router in `main.py`
```python
from app.routers import emails

app.include_router(emails.router, prefix=settings.API_V1_PREFIX)
```

---

## 🛡️ Coding & Security Conventions

1. **Keep Routers Thin**: Routers must only validate payloads, invoke services, and return responses. No SQL queries or PDF drawing directly in routers!
2. **Protect Mutation Endpoints**: Any endpoint that generates files, modifies templates, or accesses private data must declare `dependencies=[Depends(require_admin)]`.
3. **In-Memory Streaming**: Generate temporary files and ZIPs in `io.BytesIO` streams rather than writing hundreds of individual files to disk.
4. **Naming Conventions**:
   - Files: `snake_case.py` (e.g. `auth_service.py`, `email_parser.py`)
   - Classes: `PascalCase` (e.g. `AuthService`, `CanvasElement`)
   - Functions: `snake_case` (e.g. `generate_batch`, `clean_cell_value`)

---

## ☁️ How to Deploy the Backend to AWS

Here is the production-ready deployment guide for running the FastAPI backend on AWS with **EC2 (Ubuntu 22.04 LTS)**, **AWS RDS MySQL**, **Nginx**, and free **Let's Encrypt SSL**.

```text
[ Internet / Mobile QR Scanners ]
                 │
                 ▼ (HTTPS port 443)
       ┌───────────────────┐
       │   Nginx (Proxy)   │ ── SSL Termination (Certbot)
       └─────────┬─────────┘
                 │ (Internal proxy to 127.0.0.1:8000)
                 ▼
       ┌───────────────────┐
       │ FastAPI (Gunicorn │ ── Systemd daemon (auto-restarts)
       │  Uvicorn Workers) │
       └─────────┬─────────┘
                 │
                 ▼ (Port 3306 via Private Security Group)
       ┌───────────────────┐
       │   AWS RDS MySQL   │ ── Managed backups & multi-AZ
       └───────────────────┘
```

---

### Step 1: Launch an AWS EC2 Instance
1. In the AWS Console, launch an **EC2 Instance**:
   - **OS**: Ubuntu Server 22.04 LTS (HVM)
   - **Instance Type**: `t3.micro` or `t3.small` (free-tier eligible)
2. **Security Group Settings**:
   - Allow **SSH (Port 22)** from your IP
   - Allow **HTTP (Port 80)** from `0.0.0.0/0`
   - Allow **HTTPS (Port 443)** from `0.0.0.0/0`

---

### Step 2: Set Up AWS RDS MySQL Database
1. In the AWS Console, navigate to **RDS** → **Create database**.
2. Engine: **MySQL** (Community Edition, Version 8.0+).
3. Template: **Free Tier** (`db.t3.micro` or `db.t4g.micro`).
4. Set Master Username (`admin`) and Master Password.
5. In **Connectivity**:
   - VPC: Same VPC as your EC2 instance.
   - Public Access: **No** (keeps your database private from the internet!).
   - VPC Security Group: Create new, and configure its inbound rule:
     - **Type**: MYSQL/Aurora (Port 3306)
     - **Source**: Select the EC2 Security Group from Step 1.
6. Once created, copy the **RDS Endpoint** (e.g. `cert-db.c123.us-east-1.rds.amazonaws.com`).

---

### Step 3: Install System Packages on EC2
Connect to your EC2 instance via SSH:
```bash
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```
Update packages and install Python, pip, virtual environment, git, and Nginx:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git
```

---

### Step 4: Clone Backend & Install Dependencies
```bash
# Clone your backend repository
git clone https://github.com/your-username/certificate-generator-backend.git
cd certificate-generator-backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies including Gunicorn for production
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

---

### Step 5: Configure Production `.env`
Create `.env` from template:
```bash
cp .env.example .env
nano .env
```
Update with your AWS RDS MySQL credentials and production URLs:
```env
PROJECT_NAME="Universal Certificate Studio API"
API_V1_PREFIX="/api/v1"

# AWS RDS MySQL Connection String:
DATABASE_URL="mysql+pymysql://admin:YourRDSPassword@cert-db.c123.us-east-1.rds.amazonaws.com:3306/certificate_studio?charset=utf8mb4"

# Strong Random Admin Passkey:
ADMIN_SECRET_KEY="SuperSecretProductionPasskey2026!"

# Production Frontend URL (where QR code scans will redirect):
VERIFICATION_BASE_URL="https://credentials.yourdomain.com/verify?id="
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

### Step 6: Create a Systemd Background Service
To keep FastAPI running 24/7 and automatically restart on reboot, create a systemd service:

```bash
sudo nano /etc/systemd/system/certificate-studio.service
```
Paste the following configuration:
```ini
[Unit]
Description=Universal Certificate Studio FastAPI Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/certificate-generator-backend
Environment="PATH=/home/ubuntu/certificate-generator-backend/venv/bin"
ExecStart=/home/ubuntu/certificate-generator-backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start certificate-studio
sudo systemctl enable certificate-studio

# Check status:
sudo systemctl status certificate-studio
```

---

### Step 7: Configure Nginx Reverse Proxy
Edit the Nginx configuration to route public web traffic to your FastAPI application:

```bash
sudo nano /etc/nginx/sites-available/certificate-studio
```
Paste this configuration (replace `api.yourdomain.com` with your domain or EC2 Public IP):
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Allow large PDF templates and Excel participant rosters
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the site and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/certificate-studio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

### Step 8: Enable Free SSL with Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```
Certbot will automatically obtain the SSL certificate and reconfigure Nginx to enforce HTTPS.

Your API is now live at: 👉 `https://api.yourdomain.com/docs`!
