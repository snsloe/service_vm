import os
import libvirt
import uuid
from uuid import uuid4
import subprocess
import datetime


def create_vm(os_type: str, cpu_cores: int, ram_gb: int, disk_gb: int, ssh_key: str) -> str:
    """Создаёт виртуальную машину с выбранной ОС"""
    try:
        conn = libvirt.open("qemu:///system")
        if conn is None:
            raise Exception("Не удалось подключиться к QEMU")

        uuid = ""
        
        unique_id = str(uuid4())[:8]
        vm_name = f"{os_type}-vm-{unique_id}"

        disk_path = f"/var/lib/libvirt/images/{vm_name}.qcow2"


        # Создаём диск, если его нет
        if not os.path.exists(disk_path):
            assert isinstance(disk_gb, int), f"Ошибка! disk_gb не int, а {type(disk_gb)}: {disk_gb}"
            print(f"DEBUG: disk_gb = {disk_gb} (type: {type(disk_gb)})")
            disk_size = f"{int(disk_gb)}G"
            print(f"DEBUG: Форматированное значение disk_size = {disk_size}")
            print(f"Создаём диск: qemu-img create -f qcow2 {disk_path} {disk_size}")  # Лог
            print(f"DEBUG: Создаём диск командой: qemu-img create -f qcow2 {disk_path} {disk_size}")
            disk_size = f"{int(float(disk_gb))}G"
            cmd = ["qemu-img", "create", "-f", "qcow2", disk_path, disk_size]
            print(f"DEBUG: Запускаем команду: {' '.join(cmd)}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                print(f"Ошибка qemu-img: {result.stderr}")
                raise Exception(f"Ошибка создания диска {disk_path}: {result.stderr}")

            os.system(f"chown libvirt-qemu:kvm '{disk_path}'")
            os.system(f"chmod 660 '{disk_path}'")
            
            print(f"Создан виртуальный диск: {disk_path}")


        # Выбираем ISO в зависимости от ОС
        iso_paths = {
            "Debian 11": "/var/lib/libvirt/boot/debian-11.iso",
            "Ubuntu 20.04": "/var/lib/libvirt/boot/ubuntu-20.04.iso",
            "CentOS 8": "/var/lib/libvirt/boot/centos-8.iso",
        }
        iso_path = iso_paths.get(os_type)
        if not iso_path or not os.path.exists(iso_path):
            raise Exception(f"Не найден ISO-образ для {os_type}: {iso_path}")

        start_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        # XML-конфигурация ВМ

        xml_config = f"""
        <domain type='qemu'>
            <name>{vm_name}</name>
            <memory unit='GiB'>{ram_gb}</memory>
            <vcpu placement='static'>{cpu_cores}</vcpu>

            <os>
                <type arch='x86_64' machine='pc'>hvm</type>
                <boot dev='cdrom'/>
                <boot dev='hd'/>
                <acpi/>
                <apic/>
                <clock offset='utc' start='{start_time}'/>
            </os>

            <cpu mode='custom' match='exact'>
                <model fallback='allow'>qemu64</model>
            </cpu>

            <devices>
                <disk type='file' device='disk'>
                    <driver name='qemu' type='qcow2'/>
                    <source file='{disk_path}'/>
                    <target dev='vda' bus='virtio'/>
                </disk>

                <disk type='file' device='cdrom'>
                    <driver name='qemu' type='raw'/>
                    <source file='{iso_path}'/>
                    <target dev='hdc' bus='ide'/>
                    <readonly/>
                </disk>

                <interface type='network'>
                    <source network='default'/>
                    <model type='virtio'/>
                </interface>

                <serial type='pty'>
                    <target port='0'/>
                </serial>
                <console type='pty'>
                    <target type='serial' port='0'/>
                </console>

                <graphics type='vnc' port='-1' autoport='yes'/>
            </devices>
        </domain>
        """

        print(f"DEBUG: XML-конфигурация перед отправкой в libvirt:\n{xml_config}")
        dom = conn.defineXML(xml_config)
        if dom is None:
            print("DEBUG: Ошибка! ВМ не была создана в libvirt.")
            return ""

        dom.create()
        print(f"ВМ {vm_name} создана и запущена.")
        
        uuid = dom.UUIDString()
        print(f"DEBUG: Создана ВМ с UUID {uuid}")
        return uuid

    except libvirt.libvirtError as e:
        print("Ошибка libvirt:", e)
        return ""
    except Exception as e:
        print("Общая ошибка:", e)
        return ""

LIBVIRT_STATES = {
    0: "Неизвестно",
    1: "Работает",
    2: "Приостановлена",
    3: "Заблокирована",
    4: "Выключается",
    5: "Выключена",
    6: "Сломалась",
    7: "Ожидает миграции"
}

def get_active_vms():
    """Возвращает список всех ВМ с нормальными статусами"""
    try:
        conn = libvirt.open("qemu:///system")
        if conn is None:
            raise Exception("Не удалось подключиться к QEMU")

        active_vms = []
        for domain in conn.listAllDomains():
            state_code = domain.state()[0]
            active_vms.append({
                "name": domain.name(),
                "uuid": domain.UUIDString(),
                "state": LIBVIRT_STATES.get(state_code, "Неизвестно")
            })
        
        return active_vms
    except Exception as e:
        print("Ошибка получения списка ВМ:", e)
        return []


