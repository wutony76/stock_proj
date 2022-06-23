#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

  BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
  ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
  print "BASE_DIR", BASE_DIR
  print "ROOT_DIR", ROOT_DIR


  sys.path.insert(0, os.path.dirname(BASE_DIR))
  sys.path.insert(0, os.path.join(ROOT_DIR, "packages"))

  os.environ.setdefault("FATCAT_ROOT", ROOT_DIR)
  os.environ.setdefault("FATCAT_CONF", "local")

  os.environ["DJANGO_SETTINGS_MODULE"] = "demo_site1.settings"

  try:
    from django.core.management import execute_from_command_line
  except ImportError:
    # The above import may fail for some other reason. Ensure that the
    # issue is really that Django is missing to avoid masking other
    # exceptions on Python 2.
    try:
        import django
    except ImportError:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    raise

  execute_from_command_line(sys.argv)
