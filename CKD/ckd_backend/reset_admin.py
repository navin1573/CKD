import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ckd_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get the admin user
admin = User.objects.filter(username='admin').first()

if admin:
    print(f"Admin user found: {admin.username}")
    print(f"Email: {admin.email}")
    print(f"Is staff: {admin.is_staff}")
    print(f"Is superuser: {admin.is_superuser}")
    print(f"Is active: {admin.is_active}")
    
    # Reset password
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("\nPassword reset to: admin123")
    print("Staff status set to: True")
    print("Superuser status set to: True")
else:
    print("Admin user not found. Creating new admin...")
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Admin user created successfully!")
