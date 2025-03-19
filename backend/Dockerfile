FROM python:3.9-slim

# Установка системных зависимостей
RUN apt update && apt install -y \
    libvirt-dev \
    python3-dev \
    gcc \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*


ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt .


# Копирование исходного кода
COPY . .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
