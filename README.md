# Хостинг-провайдер

## Описание
Веб-сервис для аренды виртуальных машин и контейнеров с доступом по SSH.

## Установка
1. Установите Docker и Docker Compose.
2. Клонируйте репозиторий:
   ```bash
   git clone 'URL'
3. Запустите проект
   ```bash
   docker-compose up --build
4. Откройте веб-интерфейс: http://localhost:8501.

## Использование
1. Выберите тип ресурса (виртуальная машина или контейнер).
2. Настройте параметры (ОС, CPU, RAM, диск).
3. Введите SSH-ключ.
4. Нажмите "Создать".

