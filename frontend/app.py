import asyncio
import sys
import requests

# Принудительно устанавливаем политику event loop для совместимости
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Создаём event loop, если он отсутствует
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import streamlit as st  # Импортируем Streamlit после фикса asyncio

st.title("Приложение Streamlit")

st.title("Хостинг виртуальных машин и контейнеров")

resource_type = st.radio("Выберите тип ресурса:", ["Виртуальная машина", "Контейнер"])

os_type = st.selectbox("Выберите ОС:", ["Ubuntu 20.04", "CentOS 8", "Debian 11"])

cpu_cores = st.slider("Количество ядер CPU:", 1, 8, 2)
ram_gb = st.slider("Объем RAM (ГБ):", 1, 16, 4)
disk_gb = st.slider("Объем диска (ГБ):", 10, 100, 20)
ssh_key = st.text_area("Введите ваш SSH-ключ:")
shutdown_delay = st.slider("Время работы ресурса (мин):", 1, 120, 5)

if st.button("Создать"):
    payload = {
    "resource_type": resource_type,
    "os_type": os_type,
    "cpu_cores": cpu_cores,
    "ram_gb": ram_gb,
    "disk_gb": disk_gb,
    "ssh_key": ssh_key,
    "shutdown_delay": shutdown_delay
    }
    response = requests.post("http://backend:8000/create", json=payload)
    if response.status_code == 200:
        st.success("Ресурс успешно создан!")
        st.json(response.json())
    else:
        st.error("Ошибка при создании ресурса.")

st.title("Мониторинг запущенных ВМ и контейнеров")

if st.button("Обновить список"):
    response = requests.get("http://backend:8000/resources")
    if response.status_code == 200:
        data = response.json()
        st.subheader("Активные виртуальные машины")
        for vm in data["vms"]:
            st.write(f"Имя: {vm['name']}, UUID: {vm['uuid']}, Состояние: {vm['state']}")

        st.subheader("Активные контейнеры")
        for container in data["containers"]:
            st.write(f"ID: {container['id']}, Имя: {container['name']}, Статус: {container['status']}")
    else:
        st.error("Ошибка получения списка ресурсов.")
