from pydantic import BaseModel, Field

class ResourceRequest(BaseModel):
    resource_type: str
    os_type: str
    cpu_cores: int
    ram_gb: int
    disk_gb: int
    ssh_key: str
    shutdown_delay: int = Field(default=5, description="Время работы ресурса в минутах")
