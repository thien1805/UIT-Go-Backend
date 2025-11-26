# UserService - UIT-Go Backend

## Setup & Run

### 1. Prerequisites
- Docker & Docker Compose installed
- Python 3.11+

### 2. Start Database
```bash
# Start PostgreSQL
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Setup Django
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver 8001
```

### 4. Access
- API: http://localhost:8001/api/
- Admin: http://localhost:8001/admin/
- pgAdmin: http://localhost:5050/ (admin@userservice.com / admin123)

### 5. Stop Database
```bash
docker-compose down      # Stop and remove containers
docker-compose down -v   # Also remove volumes (delete data)
```

## API Endpoints

See [API_CONTRACTS.md](../../API_CONTRACTS.md)

## Environment Variables

See [.env.example](.env.example)