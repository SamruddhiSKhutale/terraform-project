# NexusTasks — Production 3-Tier Application

Modern, attractive Project & Task Management platform.

## 3-Tier Architecture

| Tier              | Technology                          |
|-------------------|-------------------------------------|
| Presentation      | Bootstrap 5, Chart.js, Custom CSS   |
| Application       | Python Flask + Gunicorn             |
| Data              | MySQL / SQLite (auto)               |

## Features

- Beautiful landing page + dark sidebar dashboard
- User registration & secure login
- Projects with color coding & progress
- Tasks with priority, status, due dates
- One-click AJAX task completion
- Live charts & stats
- Fully responsive

## Quick Start (Local / EC2)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open → http://localhost:5000  (or http://YOUR_EC2_IP:5000)

### For Production on EC2

```bash
# After cloning
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:5000 run:app
```

### Optional: Use MySQL instead of SQLite

```bash
export USE_MYSQL=true
export DB_HOST=your-mysql-host
export DB_USER=youruser
export DB_PASSWORD=yourpassword
export DB_NAME=nexustasks
```

## Project Structure

```
backend/
├── app/
│   ├── static/css/style.css
│   ├── static/js/app.js
│   ├── templates/          # All pages
│   ├── config.py
│   ├── models.py
│   └── routes.py
├── requirements.txt
└── run.py
```

That's it. Clone → install → run.
