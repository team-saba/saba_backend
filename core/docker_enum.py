from email.policy import default
from enum import Enum

class ContainerId(Enum):
    """Container ID enumeration."""
    # Docker
    DOCKER = "docker"
    # Podman
    PODMAN = "podman"
