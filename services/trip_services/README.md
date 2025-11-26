# TripService - UIT-Go Backend

## Setup & Run

### 1. Start Database
```bash
docker-compose up -d
docker-compose ps
```

### 2. Setup Django
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8002
```

### 3. Access
- API: http://localhost:8002/api/
- Admin: http://localhost:8002/admin/
- pgAdmin: http://localhost:5051/ (admin@tripservice.com / admin123)