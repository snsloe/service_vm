import docker
import os
import subprocess
import json
import uuid


def create_container(os_type: str, cpu_cores: int, ram_gb: int, disk_gb: int, ssh_key: str) -> str:
    """Создаёт Docker-контейнер через CLI"""
    try:
        print("DEBUG: Создание контейнера через Docker CLI...")
        
        image_name = {
            "Ubuntu 20.04": "ubuntu:20.04",
            "Debian 11": "debian:11",
            "CentOS 8": "centos:8"
        }.get(os_type, os_type.lower().replace(' ', '_') + ":latest")

        # Формируем корректное имя контейнера
        container_name = f"{os_type.lower().replace(' ', '_')}_container_{uuid.uuid4().hex[:8]}"

        # Проверяем, есть ли образ, если нет — загружаем
        check_image = subprocess.run(["docker", "images", "-q", image_name], capture_output=True, text=True)
        if not check_image.stdout.strip():
            print(f"Образ {image_name} не найден. Загружаем...")
            pull_result = subprocess.run(["docker", "pull", image_name], capture_output=True, text=True)
            print("Docker pull result:", pull_result.stdout, pull_result.stderr)

        # Запускаем контейнер через CLI
        command = [
            "docker", "run", "-d",
            "--memory", f"{ram_gb}g",
            "--cpu-shares", str(cpu_cores * 1024),
            "--name", container_name,  # Используем исправленное имя
            image_name, "sleep", "infinity"
        ]
        print("DEBUG: Команда для запуска контейнера:", " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"Контейнер успешно создан: {container_id}")
            return container_id
        else:
            print("Ошибка при создании контейнера:", result.stderr)
            return ""

    except Exception as e:
        print("Ошибка запуска контейнера через CLI:", str(e))
        return ""


import docker

def get_active_containers():
    """Возвращает список запущенных контейнеров"""
    try:
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        containers = client.containers.list()
        return [
            {"id": c.id, "name": c.name, "status": c.status}
            for c in containers
        ]
    except Exception as e:
        print("Ошибка получения списка контейнеров:", e)
        return []
