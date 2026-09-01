import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ckd_backend.settings')
django.setup()

from axes.models import AccessAttempt, AccessLog

# Clear all access attempts
AccessAttempt.objects.all().delete()
AccessLog.objects.all().delete()

print("All login attempt records cleared. You can now try logging in again.")
