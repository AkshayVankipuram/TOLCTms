#!C:\Python34\python.exe
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TMS.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
