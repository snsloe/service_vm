from apscheduler.schedulers.background import BackgroundScheduler
import time
import libvirt
import docker
import datetime
import xml.etree.ElementTree as ET
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
import pytz


def get_vm_start_time(domain):
    try:
        state, max_mem, mem, vcpus, cputime = domain.info()
        start_time = datetime.utcnow() - timedelta(microseconds=cputime / 1000)
        return start_time
    except Exception as e:
        print(f"Ошибка получения времени запуска ВМ {domain.name()}: {e}")
    return None

def stop_vm(uuid):
    try:
        conn = libvirt.open("qemu:///system")
        if conn is None:
            print("Ошибка: не удалось подключиться к QEMU")
            return
        domain = conn.lookupByUUIDString(uuid)
        domain.destroy()
        print(f"ВМ {uuid} остановлена")
    except Exception as e:
        print("Ошибка при остановке ВМ:", e)
    finally:
        if conn:
            conn.close()  

def stop_container(container_id):
    try:
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        container = client.containers.get(container_id)
        container.stop()
        print(f"Контейнер {container_id} остановлен")
    except Exception as e:
        print("Ошибка при остановке контейнера:", e)


def get_vm_start_time(domain):

    try:
        xml_desc = domain.XMLDesc(0)
        root = ET.fromstring(xml_desc)
        clock = root.find("./clock[@offset='utc']")
        if clock is not None and "start" in clock.attrib:
            return datetime.datetime.strptime(clock.attrib["start"], "%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        print(f"Ошибка парсинга XML ВМ {domain.name()}: {e}")
    return None

def schedule_shutdown(resource_type, resource_id, shutdown_delay):
    shutdown_time = datetime.now(moscow_tz) + timedelta(minutes=shutdown_delay)
    if resource_type == "vm":
        scheduler.add_job(stop_vm, trigger=DateTrigger(run_date=shutdown_time, timezone=moscow_tz), args=[resource_id])
    elif resource_type == "container":
        scheduler.add_job(stop_container, trigger=DateTrigger(run_date=shutdown_time, timezone=moscow_tz), args=[resource_id])


def check_resources():
    print("Запуск проверки ресурсов...")

    try:
        # Проверяем ВМ
        conn = libvirt.open("qemu:///system")
        for id in conn.listDomainsID():
            domain = conn.lookupByID(id)
            start_time = get_vm_start_time(domain)
            if start_time:
                uptime = (datetime.utcnow() - start_time).total_seconds()
                if uptime > MAX_RUNTIME_VM:
                    stop_vm(domain.UUIDString())
            else:
                print(f"Не удалось получить время запуска для ВМ {domain.name()}")

        # Проверяем контейнеры
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        for container in client.containers.list():
            try:
                started_at_str = container.attrs['State'].get('StartedAt', '')
                if not started_at_str:
                    print(f"Ошибка: контейнер {container.id} не имеет StartedAt")
                    continue

                started_at = datetime.strptime(started_at_str[:-4], "%Y-%m-%dT%H:%M:%S.%f")
                started_at = started_at.replace(tzinfo=pytz.UTC)  
                uptime = (datetime.utcnow().replace(tzinfo=pytz.UTC) - started_at).total_seconds()

                if uptime > MAX_RUNTIME_CONTAINER:
                    stop_container(container.id)
            except Exception as e:
                print(f"Ошибка обработки контейнера {container.id}: {e}")

    except Exception as e:
        print("Ошибка мониторинга:", e)




scheduler = BackgroundScheduler()
scheduler.start()

moscow_tz = pytz.timezone("Europe/Moscow")

#shutdown_time = datetime.now(moscow_tz) + timedelta(minutes=10) 

scheduler.add_job(stop_vm, trigger=DateTrigger(run_date=shutdown_time, timezone=moscow_tz), args=[vm_uuid])


scheduler.add_job(stop_container, trigger=DateTrigger(run_date=shutdown_time, timezone=moscow_tz), args=[container_id])
