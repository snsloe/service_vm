from fastapi import FastAPI
from models.resource import ResourceRequest
from services.qemu_service import create_vm
from services.docker_service import create_container
from services.qemu_service import get_active_vms
from services.docker_service import get_active_containers
import threading
from services.monitor_service import scheduler
from services.monitor_service import schedule_shutdown
import time
print("Текущее время Python:", time.strftime("%Y-%m-%d %H:%M:%S %Z"))

import os

os.environ['TZ'] = 'Europe/Moscow'
time.tzset()

print("Текущее время Python:", time.strftime("%Y-%m-%d %H:%M:%S %Z"))

app = FastAPI()

# threading.Thread(target=monitor_resources, daemon=True).start()

@app.post("/create")
async def create_resource(request: ResourceRequest):
    if request.resource_type == "Виртуальная машина":
        vm_id = create_vm(request.os_type, request.cpu_cores, request.ram_gb, request.disk_gb, request.ssh_key)
        schedule_shutdown("vm", vm_id, request.shutdown_delay)  # Передаём vm_id как resource_id
        return {"message": "Виртуальная машина создана", "vm_id": vm_id}
    elif request.resource_type == "Контейнер":
        container_id = create_container(request.os_type, request.cpu_cores, request.ram_gb, request.disk_gb, request.ssh_key)
        schedule_shutdown("container", container_id, request.shutdown_delay)  # Передаём container_id как resource_id
        return {"message": "Контейнер создан", "container_id": container_id}
    else:
        return {"error": "Неверный тип ресурса"}


@app.get("/resources")
async def list_active_resources():
    vms = get_active_vms()
    containers = get_active_containers()
    return {"vms": vms, "containers": containers}



