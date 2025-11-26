# 🚀 Quick Start - UIT-Go Backend

Hướng dẫn nhanh để chạy project trong 5 phút!

---

## ⚡ Chạy với Docker (Recommended)

### 1. Clone & Setup

```bash
cd "SE360 UIT-GO"

# Tạo .env file
cat > .env << 'EOF'
SECRET_KEY=django-insecure-dev-key-change-in-production
JWT_SECRET=your-jwt-secret-key-change-in-production
INTERNAL_SERVICE_TOKEN=internal-service-token-dev
USER_DB_NAME=user_service
USER_DB_USER=postgres
USER_DB_PASSWORD=postgres123
TRIP_DB_NAME=trip_service
TRIP_DB_USER=postgres
TRIP_DB_PASSWORD=postgres123
ALLOWED_HOSTS=*
PGADMIN_EMAIL=admin@uitgo.com
PGADMIN_PASSWORD=admin123
EOF
```

### 2. Start Services

```bash
# Build và start
docker-compose up --build

# Chờ services khởi động (~30 giây)
```

### 3. Run Migrations (Terminal mới)

```bash
docker-compose exec user-service python manage.py migrate
docker-compose exec trip-service python manage.py migrate
```

### 4. Create Admin

```bash
docker-compose exec user-service python manage.py createsuperuser
# Email: admin@uitgo.com
# Password: admin123
```

### 5. Test APIs

```bash
# User Service
curl http://localhost:8001/api/auth/

# Trip Service
curl http://localhost:8002/api/trips/
```

✅ **Done!** Services running at:
- User: http://localhost:8001
- Trip: http://localhost:8002
- pgAdmin: http://localhost:5050

---

## 💻 Chạy Local (Development)

### 1. Setup PostgreSQL

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create databases
psql -U postgres -c "CREATE DATABASE user_service;"
psql -U postgres -c "CREATE DATABASE trip_service;"
```

### 2. User Service

```bash
cd services/user_service

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# .env file
cat > .env << 'EOF'
DB_NAME=user_service
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=dev-key
JWT_SECRET=jwt-secret
INTERNAL_SERVICE_TOKEN=token
ALLOWED_HOSTS=*
TRIP_SERVICE_URL=http://localhost:8002
EOF

# Migrate & Run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

### 3. Trip Service (New Terminal)

```bash
cd services/trip_services
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cat > .env << 'EOF'
DB_NAME=trip_service
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=dev-key
JWT_SECRET=jwt-secret
INTERNAL_SERVICE_TOKEN=token
ALLOWED_HOSTS=*
USER_SERVICE_URL=http://localhost:8001
EOF

python manage.py migrate
python manage.py runserver 8002
```

---

## 🧪 Test Flow

### 1. Đăng ký Passenger

```bash
curl -X POST http://localhost:8001/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger@test.com",
    "password": "Test123456",
    "full_name": "Test Passenger",
    "phone": "0901234567",
    "user_type": "passenger"
  }'

# Lưu access_token
```

### 2. Đăng ký Driver

```bash
# a. Đăng ký account
curl -X POST http://localhost:8001/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "driver@test.com",
    "password": "Test123456",
    "full_name": "Test Driver",
    "phone": "0909876543",
    "user_type": "driver"
  }'

# b. Đăng ký driver profile
curl -X POST http://localhost:8001/api/drivers/register/ \
  -H "Authorization: Bearer <driver_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_type": "bike",
    "license_plate": "59A-12345",
    "vehicle_model": "Honda Wave",
    "vehicle_color": "Đỏ",
    "driver_license": "123456789",
    "vehicle_registration": "REG123"
  }'

# c. Set online
curl -X PUT http://localhost:8001/api/drivers/me/status/ \
  -H "Authorization: Bearer <driver_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_online": true,
    "latitude": 10.762622,
    "longitude": 106.660172
  }'
```

### 3. Admin approve driver

```bash
# Login admin
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@uitgo.com",
    "password": "admin123"
  }'

# Get drivers
curl http://localhost:8001/api/admin/drivers/ \
  -H "Authorization: Bearer <admin_token>"

# Approve driver
curl -X PUT http://localhost:8001/api/admin/drivers/<driver_id>/approve/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "approval_note": "OK"
  }'
```

### 4. Tạo Trip

```bash
curl -X POST http://localhost:8002/api/trips/ \
  -H "Authorization: Bearer <passenger_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_lat": 10.762622,
    "pickup_lng": 106.660172,
    "pickup_address": "UIT",
    "dropoff_lat": 10.771513,
    "dropoff_lng": 106.698660,
    "dropoff_address": "Tao Đàn",
    "vehicle_type": "bike",
    "payment_method": "cash"
  }'
```

**Response sẽ bao gồm:**
- ✅ Trip info
- ✅ Estimated fare
- ✅ Available drivers
- ✅ Distance calculation

---

## 📊 pgAdmin Setup (Optional)

1. Open http://localhost:5050
2. Login: `admin@uitgo.com` / `admin123`
3. Add Server:
   - Name: `User DB`
   - Host: `user-db` (Docker) hoặc `localhost` (Local)
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres123`

---

## 🛠️ Common Commands

### Docker

```bash
# Stop services
docker-compose down

# Restart service
docker-compose restart user-service

# View logs
docker-compose logs -f user-service

# Shell access
docker-compose exec user-service bash

# Rebuild
docker-compose up --build
```

### Django Management

```bash
# Trong container
docker-compose exec user-service python manage.py <command>

# Local
python manage.py <command>

# Common commands:
# - migrate
# - makemigrations
# - createsuperuser
# - shell
# - dbshell
```

---

## ❓ Troubleshooting

### Port already in use

```bash
# Kill process
lsof -i :8001
kill -9 <PID>
```

### Database connection error

```bash
# Check database
docker-compose ps
docker-compose logs user-db

# Restart
docker-compose restart user-db
```

### Module not found

```bash
# Docker: Rebuild
docker-compose up --build

# Local: Reinstall
pip install -r requirements.txt
```

---

## 📚 Full Documentation

Xem `README.md` để biết chi tiết về:
- Architecture
- All API endpoints
- Advanced testing
- Production deployment

---

**Happy Coding! 🚀**
