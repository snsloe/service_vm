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

RUN pip uninstall -y docker docker-py && pip install --no-cache-dir docker
# Копирование и установка Python-зависимостей
RUN pip uninstall -y docker-py docker && pip install --no-cache-dir docker
COPY requirements.txt .
RUN apt update && apt install -y sudo
RUN apt-get update && apt-get install -y qemu-utils
RUN apt update && apt install -y docker.io
RUN pip install --no-cache-dir -r requirements.txt
RUN groupadd -g 64055 kvm && useradd -u 64055 -g kvm libvirt-qemu

# Копирование исходного кода
COPY . .

# Запуск FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
