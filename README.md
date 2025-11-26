# 🚗 UIT-Go Backend - Ride Hailing Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

Hệ thống backend cho ứng dụng đặt xe UIT-Go, xây dựng theo kiến trúc **Microservices** với Django REST Framework.

---

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Chạy ứng dụng](#-chạy-ứng-dụng)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing)
- [Tính năng](#-tính-năng)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)

---

## 🎯 Tổng quan

**UIT-Go** là nền tảng đặt xe trực tuyến tương tự Grab/Uber, được xây dựng với:

- **Microservices Architecture**: Các services độc lập, dễ scale
- **Django REST Framework**: API RESTful mạnh mẽ
- **JWT Authentication**: Bảo mật với JSON Web Tokens
- **PostgreSQL**: Database quan hệ hiệu năng cao
- **Docker**: Containerization để deploy dễ dàng

### Các Services

| Service | Port | Mô tả |
|---------|------|-------|
| **User Service** | 8001 | Quản lý authentication, users, drivers |
| **Trip Service** | 8002 | Quản lý trips, bookings, matching |
| **User Database** | 5432 | PostgreSQL cho User Service |
| **Trip Database** | 5433 | PostgreSQL cho Trip Service |
| **pgAdmin** | 5050 | Web interface quản lý databases |

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                       Client Applications                        │
│            (Mobile App, Web App, Admin Dashboard)                │
└─────────────────────────────────────────────────────────────────┘
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway (Future)                       │
│                   Load Balancing & Routing                       │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  User Service    │◄────────────────►│  Trip Service    │
│   Port: 8001     │   Internal API   │   Port: 8002     │
├──────────────────┤                  ├──────────────────┤
│ • Authentication │                  │ • Trip Creation  │
│ • User Profiles  │                  │ • Trip Tracking  │
│ • Driver Mgmt    │                  │ • Trip Matching  │
│ • Admin Panel    │                  │ • Pricing Calc   │
└────────┬─────────┘                  └─────────┬────────┘
         │                                      │
         ▼                                      ▼
┌──────────────────┐                  ┌──────────────────┐
│   User DB        │                  │   Trip DB        │
│ PostgreSQL:5432  │                  │ PostgreSQL:5433  │
└──────────────────┘                  └──────────────────┘
```

---

## 💻 Yêu cầu hệ thống

### Phiên bản cần thiết

- **Python**: 3.11+
- **Docker**: 20.10+ và Docker Compose 2.0+
- **PostgreSQL**: 15+ (nếu chạy local)
- **Git**: Để clone repository

### Kiến thức cần có

- Python & Django cơ bản
- REST API concepts
- Docker basics (recommended)
- PostgreSQL/SQL cơ bản

---

## 🚀 Cài đặt

### Option 1: Chạy với Docker (Recommended) ⭐

**Bước 1: Clone repository**

```bash
git clone <repository-url>
cd "SE360 UIT-GO"
```

**Bước 2: Tạo file `.env`**

```bash
# Copy từ template
cp .env.example .env

# Hoặc tạo mới với nano/vim
nano .env
```

Nội dung file `.env` tối thiểu:

```bash
# Security
SECRET_KEY=your-django-secret-key-here
JWT_SECRET=your-jwt-secret-key-here
INTERNAL_SERVICE_TOKEN=your-internal-service-token-here

# Databases
USER_DB_NAME=user_service
USER_DB_USER=postgres
USER_DB_PASSWORD=postgres123

TRIP_DB_NAME=trip_service
TRIP_DB_USER=postgres
TRIP_DB_PASSWORD=postgres123

# CORS
ALLOWED_HOSTS=*

# pgAdmin (optional)
PGADMIN_EMAIL=admin@uitgo.com
PGADMIN_PASSWORD=admin123
```

**Bước 3: Generate secret keys**

```bash
# Django SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# JWT_SECRET (64 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# INTERNAL_SERVICE_TOKEN (32 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy các giá trị này vào file `.env`.

**Bước 4: Build và start services**

```bash
# Build và start tất cả services
docker-compose up --build

# Hoặc chạy background
docker-compose up --build -d

# Xem logs
docker-compose logs -f
```

**Bước 5: Chạy migrations**

```bash
# Terminal mới (nếu chạy -d)
docker-compose exec user-service python manage.py migrate
docker-compose exec trip-service python manage.py migrate
```

**Bước 6: Tạo superuser (admin)**

```bash
docker-compose exec user-service python manage.py createsuperuser

# Nhập thông tin:
# Email: admin@uitgo.com
# Password: admin123
# Full name: Admin
```

**Bước 7: Verify services**

```bash
# User Service
curl http://localhost:8001/api/auth/

# Trip Service
curl http://localhost:8002/api/trips/

# pgAdmin (browser)
http://localhost:5050
```

✅ **Done!** Services đang chạy ở:
- User Service: http://localhost:8001
- Trip Service: http://localhost:8002
- pgAdmin: http://localhost:5050

---

### Option 2: Chạy Local (Development)

**Bước 1: Clone repository**

```bash
git clone <repository-url>
cd "SE360 UIT-GO"
```

**Bước 2: Cài đặt PostgreSQL**

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15
sudo systemctl start postgresql

# Windows: Download từ https://www.postgresql.org/download/windows/
```

**Bước 3: Tạo databases**

```bash
psql -U postgres

# Trong psql shell:
CREATE DATABASE user_service;
CREATE DATABASE trip_service;
\q
```

**Bước 4: Setup User Service**

```bash
cd services/user_service

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Cài dependencies
pip install -r requirements.txt

# Tạo file .env
cat > .env << 'EOF'
DB_NAME=user_service
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your-django-secret-key-here
JWT_SECRET=your-jwt-secret-key-here
INTERNAL_SERVICE_TOKEN=your-internal-service-token-here
ALLOWED_HOSTS=*
TRIP_SERVICE_URL=http://localhost:8002
EOF

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver 8001
```

**Bước 5: Setup Trip Service (Terminal mới)**

```bash
cd services/trip_services

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt

# Tạo file .env
cat > .env << 'EOF'
DB_NAME=trip_service
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your-django-secret-key-here
JWT_SECRET=your-jwt-secret-key-here
INTERNAL_SERVICE_TOKEN=your-internal-service-token-here
ALLOWED_HOSTS=*
USER_SERVICE_URL=http://localhost:8001
EOF

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver 8002
```

**Bước 6: Verify**

```bash
# User Service
curl http://localhost:8001/api/auth/

# Trip Service
curl http://localhost:8002/api/trips/
```

---

## 🎮 Chạy ứng dụng

### Với Docker

```bash
# Start tất cả services
docker-compose up

# Start + rebuild
docker-compose up --build

# Start background
docker-compose up -d

# Stop services
docker-compose down

# Stop và xóa volumes (⚠️ mất data)
docker-compose down -v

# Xem logs
docker-compose logs -f user-service
docker-compose logs -f trip-service

# Restart một service
docker-compose restart user-service

# Exec vào container
docker-compose exec user-service bash
```

### Local Development

```bash
# Terminal 1: User Service
cd services/user_service
source venv/bin/activate
python manage.py runserver 8001

# Terminal 2: Trip Service
cd services/trip_services
source venv/bin/activate
python manage.py runserver 8002
```

---

## 📡 API Endpoints

### 🔐 Authentication API (User Service - Port 8001)

#### Đăng ký

```bash
POST http://localhost:8001/api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "Nguyễn Văn A",
  "phone": "0901234567",
  "user_type": "passenger"  # passenger hoặc driver
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "Nguyễn Văn A",
      "user_type": "passenger"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  },
  "message": "Đăng ký thành công"
}
```

#### Đăng nhập

```bash
POST http://localhost:8001/api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Lấy thông tin user hiện tại

```bash
GET http://localhost:8001/api/auth/me/
Authorization: Bearer <access_token>
```

#### Refresh token

```bash
POST http://localhost:8001/api/auth/refresh-token/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

#### Đăng xuất

```bash
POST http://localhost:8001/api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

### 🚗 Driver API (User Service - Port 8001)

#### Đăng ký thông tin driver

```bash
POST http://localhost:8001/api/drivers/register/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "vehicle_type": "bike",  # bike, car_4seats, car_7seats
  "license_plate": "59A-12345",
  "vehicle_model": "Honda Wave",
  "vehicle_color": "Đỏ",
  "driver_license": "123456789",
  "vehicle_registration": "REG123456"
}
```

#### Lấy thông tin driver profile

```bash
# Driver của chính mình
GET http://localhost:8001/api/drivers/me/profile/
Authorization: Bearer <access_token>

# Driver khác (public info)
GET http://localhost:8001/api/drivers/<driver_id>/profile/
```

#### Cập nhật trạng thái online/offline

```bash
PUT http://localhost:8001/api/drivers/me/status/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "is_online": true,
  "latitude": 10.762622,
  "longitude": 106.660172
}
```

---

### 🚕 Trip API (Trip Service - Port 8002)

#### Tạo trip mới (Passenger)

```bash
POST http://localhost:8002/api/trips/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "pickup_lat": 10.762622,
  "pickup_lng": 106.660172,
  "pickup_address": "Đại học Công nghệ Thông tin, ĐHQG TP.HCM",
  "dropoff_lat": 10.771513,
  "dropoff_lng": 106.698660,
  "dropoff_address": "Công viên Tao Đàn",
  "vehicle_type": "bike",
  "payment_method": "cash"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "trip": {
      "id": "uuid",
      "status": "finding_driver",
      "distance_km": 4.2,
      "estimated_fare": 25000,
      "base_fare": 10000,
      "distance_fare": 12600,
      "surge_multiplier": 1.0,
      "available_drivers": [
        {
          "driver_id": "uuid",
          "distance_to_pickup": 1.5,
          "rating": 4.8
        }
      ]
    }
  },
  "message": "Tạo chuyến đi thành công"
}
```

#### Lấy danh sách trips

```bash
# Trips của passenger
GET http://localhost:8002/api/trips/?role=passenger&page=1&page_size=20
Authorization: Bearer <access_token>

# Trips của driver
GET http://localhost:8002/api/trips/?role=driver&page=1&page_size=20
Authorization: Bearer <access_token>
```

#### Lấy chi tiết trip

```bash
GET http://localhost:8002/api/trips/<trip_id>/
Authorization: Bearer <access_token>
```

#### Cập nhật trạng thái trip

```bash
PUT http://localhost:8002/api/trips/<trip_id>/status/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "driver_arriving"
  # Các status: finding_driver, driver_assigned, driver_arriving,
  #             passenger_picked_up, completed, cancelled_by_passenger, etc.
}
```

#### Driver nhận trip

```bash
PUT http://localhost:8002/api/trips/<trip_id>/assign-driver/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "driver_id": "<driver_uuid>"
}
```

#### Lấy trips khả dụng (cho Driver)

```bash
GET http://localhost:8002/api/trips/available/?vehicle_type=bike
Authorization: Bearer <access_token>
```

---

### 👨‍💼 Admin API (User Service - Port 8001)

#### Dashboard statistics

```bash
GET http://localhost:8001/api/admin/dashboard/stats/
Authorization: Bearer <admin_access_token>
```

**Response:**

```json
{
  "success": true,
  "data": {
    "users": {
      "total": 1250,
      "passengers": 1000,
      "drivers": 250,
      "new_last_7days": 45
    },
    "drivers": {
      "total": 250,
      "pending_approval": 10,
      "approved": 230,
      "currently_online": 85
    }
  }
}
```

#### Quản lý users

```bash
# Danh sách users
GET http://localhost:8001/api/admin/users/?user_type=passenger&search=nguyen&page=1
Authorization: Bearer <admin_access_token>

# Xóa user (soft delete)
DELETE http://localhost:8001/api/admin/users/<user_id>/
Authorization: Bearer <admin_access_token>
```

#### Quản lý drivers

```bash
# Danh sách drivers
GET http://localhost:8001/api/admin/drivers/?approval_status=pending&page=1
Authorization: Bearer <admin_access_token>

# Duyệt/Từ chối driver
PUT http://localhost:8001/api/admin/drivers/<driver_id>/approve/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "action": "approve",  # approve, reject, suspend
  "approval_note": "Đã kiểm tra đầy đủ giấy tờ"
}
```

---

## 🧪 Testing

### 1. Test Authentication Flow

```bash
# 1. Đăng ký passenger
curl -X POST http://localhost:8001/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger1@example.com",
    "password": "Test123456",
    "full_name": "Nguyễn Văn A",
    "phone": "0901234567",
    "user_type": "passenger"
  }'

# Lưu access_token từ response

# 2. Đăng nhập
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "passenger1@example.com",
    "password": "Test123456"
  }'

# 3. Lấy thông tin user
curl http://localhost:8001/api/auth/me/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 2. Test Driver Registration

```bash
# 1. Đăng ký driver account
curl -X POST http://localhost:8001/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "driver1@example.com",
    "password": "Test123456",
    "full_name": "Trần Văn B",
    "phone": "0909876543",
    "user_type": "driver"
  }'

# 2. Đăng ký driver profile
curl -X POST http://localhost:8001/api/drivers/register/ \
  -H "Authorization: Bearer <driver_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_type": "bike",
    "license_plate": "59A-12345",
    "vehicle_model": "Honda Wave",
    "vehicle_color": "Đỏ",
    "driver_license": "123456789",
    "vehicle_registration": "REG123"
  }'

# 3. Update status online
curl -X PUT http://localhost:8001/api/drivers/me/status/ \
  -H "Authorization: Bearer <driver_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_online": true,
    "latitude": 10.762622,
    "longitude": 106.660172
  }'
```

### 3. Test Trip Creation & Matching

```bash
# 1. Passenger tạo trip
curl -X POST http://localhost:8002/api/trips/ \
  -H "Authorization: Bearer <passenger_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_lat": 10.762622,
    "pickup_lng": 106.660172,
    "pickup_address": "UIT, ĐHQG TP.HCM",
    "dropoff_lat": 10.771513,
    "dropoff_lng": 106.698660,
    "dropoff_address": "Công viên Tao Đàn",
    "vehicle_type": "bike",
    "payment_method": "cash"
  }'

# Lưu trip_id từ response

# 2. Driver xem trips khả dụng
curl http://localhost:8002/api/trips/available/?vehicle_type=bike \
  -H "Authorization: Bearer <driver_access_token>"

# 3. Driver nhận trip
curl -X PUT http://localhost:8002/api/trips/<trip_id>/assign-driver/ \
  -H "Authorization: Bearer <driver_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "driver_id": "<driver_uuid>"
  }'

# 4. Cập nhật trạng thái trip
curl -X PUT http://localhost:8002/api/trips/<trip_id>/status/ \
  -H "Authorization: Bearer <driver_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "passenger_picked_up"
  }'
```

### 4. Test Admin Functions

```bash
# 1. Admin login
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@uitgo.com",
    "password": "admin123"
  }'

# 2. Dashboard stats
curl http://localhost:8001/api/admin/dashboard/stats/ \
  -H "Authorization: Bearer <admin_access_token>"

# 3. Danh sách drivers pending
curl "http://localhost:8001/api/admin/drivers/?approval_status=pending" \
  -H "Authorization: Bearer <admin_access_token>"

# 4. Approve driver
curl -X PUT http://localhost:8001/api/admin/drivers/<driver_id>/approve/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "approval_note": "Approved"
  }'
```

### 5. Test với Python Script

Tạo file `test_api.py`:

```python
import requests
import json

BASE_URL_USER = "http://localhost:8001"
BASE_URL_TRIP = "http://localhost:8002"

# 1. Register Passenger
response = requests.post(f"{BASE_URL_USER}/api/auth/register/", json={
    "email": "test_passenger@example.com",
    "password": "Test123456",
    "full_name": "Test Passenger",
    "phone": "0901234567",
    "user_type": "passenger"
})
print("Register:", response.json())
passenger_token = response.json()['data']['tokens']['access']

# 2. Create Trip
response = requests.post(f"{BASE_URL_TRIP}/api/trips/", 
    headers={"Authorization": f"Bearer {passenger_token}"},
    json={
        "pickup_lat": 10.762622,
        "pickup_lng": 106.660172,
        "pickup_address": "UIT",
        "dropoff_lat": 10.771513,
        "dropoff_lng": 106.698660,
        "dropoff_address": "Tao Đàn",
        "vehicle_type": "bike",
        "payment_method": "cash"
    }
)
print("Create Trip:", response.json())
```

Chạy:

```bash
python test_api.py
```

---

## ✨ Tính năng

### ✅ Đã hoàn thành

#### Authentication & Authorization
- ✅ Đăng ký tài khoản (Passenger/Driver)
- ✅ Đăng nhập với JWT
- ✅ Refresh token
- ✅ Đăng xuất
- ✅ Lấy thông tin user hiện tại
- ✅ Role-based access (Passenger/Driver/Admin)

#### User Management
- ✅ Profile management
- ✅ User CRUD operations
- ✅ Soft delete users

#### Driver Management
- ✅ Driver registration với thông tin xe
- ✅ Driver profile (public/private)
- ✅ Cập nhật trạng thái online/offline
- ✅ Cập nhật vị trí real-time
- ✅ Driver approval workflow (pending/approved/rejected)
- ✅ Lưu thông tin xe và giấy tờ

#### Trip Management
- ✅ Tạo trip mới
- ✅ Lấy danh sách trips (có phân trang)
- ✅ Chi tiết trip
- ✅ Cập nhật trạng thái trip
- ✅ Trip status tracking (8 trạng thái)
- ✅ Hủy trip

#### Driver Matching Algorithm
- ✅ Tìm driver gần pickup location
- ✅ Filter theo vehicle type
- ✅ Tính khoảng cách với Haversine formula
- ✅ Sort theo khoảng cách
- ✅ Chỉ match driver online & approved

#### Pricing Calculator
- ✅ Tính giá theo khoảng cách
- ✅ Base fare + distance fare
- ✅ Surge pricing (giờ cao điểm)
- ✅ Khác giá theo loại xe
- ✅ Breakdown chi tiết giá

#### Admin Panel API
- ✅ Dashboard statistics
- ✅ User management (list, search, delete)
- ✅ Driver management (list, search, approve/reject)
- ✅ Filter & search functions
- ✅ Pagination
- ✅ Permission checks (staff/superuser only)

#### Technical
- ✅ Microservices architecture
- ✅ Service-to-service authentication (INTERNAL_SERVICE_TOKEN)
- ✅ Docker containerization
- ✅ PostgreSQL databases
- ✅ Middleware cho JWT validation
- ✅ Custom pagination
- ✅ Error handling chuẩn
- ✅ Vietnamese comments

### 🚧 Cần phát triển thêm

- ⏳ Real-time notifications (WebSocket)
- ⏳ Payment integration
- ⏳ Rating & Review system
- ⏳ Trip history với filters nâng cao
- ⏳ Analytics & Reporting
- ⏳ Push notifications
- ⏳ Chat giữa passenger và driver
- ⏳ Promo codes & Discounts
- ⏳ Multi-language support
- ⏳ API Gateway với rate limiting
- ⏳ Caching layer (Redis)
- ⏳ Message queue (RabbitMQ/Kafka)

---

## 📁 Cấu trúc thư mục

```
SE360 UIT-GO/
├── services/
│   ├── user_service/           # User & Driver Service
│   │   ├── authentication/     # Authentication app
│   │   │   ├── models.py      # User model
│   │   │   ├── views.py       # Auth endpoints
│   │   │   ├── serializers.py # Auth serializers
│   │   │   ├── urls.py        # Auth URLs
│   │   │   ├── admin_views.py # Admin panel endpoints
│   │   │   └── admin_urls.py  # Admin URLs
│   │   ├── drivers/           # Driver app
│   │   │   ├── models.py      # DriverProfile model
│   │   │   ├── views.py       # Driver endpoints
│   │   │   ├── serializers.py # Driver serializers
│   │   │   └── urls.py        # Driver URLs
│   │   ├── user_service/      # Django settings
│   │   │   ├── settings.py    # Config
│   │   │   ├── urls.py        # Main URLs
│   │   │   └── middleware.py  # JWT middleware
│   │   ├── Dockerfile         # Docker config
│   │   ├── requirements.txt   # Python dependencies
│   │   ├── docker-compose.yml # Local docker-compose
│   │   └── manage.py          # Django management
│   │
│   └── trip_services/          # Trip Service
│       ├── trips/             # Trip app
│       │   ├── models.py      # Trip model
│       │   ├── views.py       # Trip endpoints
│       │   ├── serializers.py # Trip serializers
│       │   ├── urls.py        # Trip URLs
│       │   ├── pagination.py  # Custom pagination
│       │   ├── matching.py    # Driver matching algorithm
│       │   └── pricing.py     # Pricing calculator
│       ├── trip_services/     # Django settings
│       │   ├── settings.py    # Config
│       │   ├── urls.py        # Main URLs
│       │   └── middleware.py  # JWT middleware
│       ├── Dockerfile         # Docker config
│       ├── requirements.txt   # Python dependencies
│       ├── docker-compose.yml # Local docker-compose
│       └── manage.py          # Django management
│
├── docker-compose.yml         # Root orchestration
├── .env.example               # Environment template
├── .gitignore                 # Git ignore
└── README.md                  # This file
```

---

## 🔧 Troubleshooting

### Lỗi: Port already in use

```bash
# Tìm process đang dùng port
lsof -i :8001
lsof -i :5432

# Kill process
kill -9 <PID>

# Hoặc thay đổi port trong docker-compose.yml
```

### Lỗi: Database connection refused

```bash
# Kiểm tra database container
docker-compose ps

# Restart database
docker-compose restart user-db trip-db

# Xem logs database
docker-compose logs user-db
```

### Lỗi: ModuleNotFoundError

```bash
# Với Docker: Rebuild
docker-compose up --build

# Local: Reinstall dependencies
pip install -r requirements.txt
```

### Lỗi: Migration conflicts

```bash
# Reset migrations (⚠️ mất data)
docker-compose down -v
docker-compose up --build
```

### Lỗi: Permission denied in Docker

```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📚 Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [JWT Introduction](https://jwt.io/introduction)

---

## 👥 Team

**UIT-Go Development Team**

- Backend: Django REST Framework
- Database: PostgreSQL
- DevOps: Docker

---

## 📄 License

This project is for educational purposes.

---
