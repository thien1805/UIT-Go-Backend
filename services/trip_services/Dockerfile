# ==========================================
# Dockerfile cho Trip Service - UIT-Go Backend
# ==========================================

# Sử dụng Python 3.11 official image làm base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="UIT-Go Team"
LABEL service="trip-service"
LABEL version="1.0"

# Set environment variables
# Ngăn Python tạo .pyc files (bytecode)
ENV PYTHONDONTWRITEBYTECODE=1
# Ngăn Python buffer output (logs xuất hiện real-time)
ENV PYTHONUNBUFFERED=1

# Tạo thư mục làm việc trong container
WORKDIR /app

# Cài đặt system dependencies cần thiết
# postgresql-client: để kết nối với PostgreSQL
# gcc, python3-dev, musl-dev: để build một số Python packages
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt trước để tận dụng Docker cache
# Nếu requirements.txt không thay đổi, Docker sẽ cache layer này
COPY requirements.txt .

# Upgrade pip và cài đặt dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Tạo thư mục cho static files và media files
RUN mkdir -p /app/staticfiles /app/mediafiles

# Expose port 8002 (Trip Service)
EXPOSE 8002

# Script để chạy migrations và start server
# Tạo script entrypoint
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "⏳ Đợi database sẵn sàng..."\n\
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do\n\
  echo "Database chưa sẵn sàng, đợi 2 giây..."\n\
  sleep 2\n\
done\n\
\n\
echo "✅ Database đã sẵn sàng!"\n\
\n\
echo "🔄 Chạy migrations..."\n\
python manage.py migrate --noinput\n\
\n\
echo "📦 Thu thập static files..."\n\
python manage.py collectstatic --noinput --clear || true\n\
\n\
echo "🚀 Khởi động Trip Service trên port 8002..."\n\
python manage.py runserver 0.0.0.0:8002\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

