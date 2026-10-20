"""Direct Mode stable GenVM SDK pin; Windows fd0 compatibility only in tests."""
import os
from gltest.direct import loader, sdk_loader

sdk_loader.get_latest_version=lambda: 'v0.2.12'
_original=loader._inject_message_to_fd0

def safe_inject(vm):
    try:
        return _original(vm)
    except PermissionError:
        if os.name!='nt':
            raise
        return None

loader._inject_message_to_fd0=safe_inject
