# Base image สำหรับ Python 3.9 slim
FROM python:3.9-slim

# ติดตั้ง ping สำหรับการทดสอบเครือข่าย
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

# กำหนด working directory ภายใน container
WORKDIR /app

# คัดลอกไฟล์ dependency จากโฮสต์ไปยัง container
COPY app/requirements.txt .

# ติดตั้งไลบรารีที่จำเป็น
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดแอปพลิเคชันทั้งหมด
COPY app/ .

# เปิดพอร์ตสำหรับ Flask
EXPOSE 5000

# รันแอปพลิเคชัน
CMD ["python", "app.py"]