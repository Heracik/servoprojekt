import os
import sys
import threading
from mqtt_thread import start_mqtt

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mqtt_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    #mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    #mqtt_thread.start()

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
