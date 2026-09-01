import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ckd_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if superuser already exists
if User.objects.filter(username='admin').exists():
    print("Superuser 'admin' already exists.")
else:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created successfully!")
    print("Username: admin")
    print("Password: admin123")
