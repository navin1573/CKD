from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'System Administrator'),
        ('DOCTOR', 'Medical Doctor'),
        ('PATIENT', 'Patient User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT')
    email = models.EmailField(unique=True, db_index=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialization})"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    medical_history_summary = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Prediction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='predictions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_predictions')
    prediction_date = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # 24 Clinical Features from UCI Dataset
    age = models.FloatField(null=True, blank=True)
    bp = models.FloatField(null=True, blank=True)
    sg = models.FloatField(null=True, blank=True)
    al = models.FloatField(null=True, blank=True)
    su = models.FloatField(null=True, blank=True)
    rbc = models.CharField(max_length=20, null=True, blank=True)
    pc = models.CharField(max_length=20, null=True, blank=True)
    pcc = models.CharField(max_length=20, null=True, blank=True)
    ba = models.CharField(max_length=20, null=True, blank=True)
    bgr = models.FloatField(null=True, blank=True)
    bu = models.FloatField(null=True, blank=True)
    sc = models.FloatField(null=True, blank=True)
    sod = models.FloatField(null=True, blank=True)
    pot = models.FloatField(null=True, blank=True)
    hemo = models.FloatField(null=True, blank=True)
    pcv = models.FloatField(null=True, blank=True)
    wc = models.FloatField(null=True, blank=True)
    rc = models.FloatField(null=True, blank=True)
    htn = models.CharField(max_length=10, null=True, blank=True)
    dm = models.CharField(max_length=10, null=True, blank=True)
    cad = models.CharField(max_length=10, null=True, blank=True)
    appet = models.CharField(max_length=20, null=True, blank=True)
    pe = models.CharField(max_length=10, null=True, blank=True)
    ane = models.CharField(max_length=10, null=True, blank=True)
    
    # Diagnosis Outputs
    predicted_class = models.CharField(max_length=20)  # 'ckd' or 'notckd'
    prediction_probability = models.FloatField()
    risk_level = models.CharField(max_length=20)  # 'LOW', 'MEDIUM', 'HIGH'

    def __str__(self):
        return f"Prediction for {self.patient} on {self.prediction_date.strftime('%Y-%m-%d')} - {self.risk_level}"


class Explanation(models.Model):
    prediction = models.OneToOneField(Prediction, on_delete=models.CASCADE, related_name='explanation')
    shap_values_json = models.TextField()  # Stores serialized list of SHAP contributions
    lime_explanations_json = models.TextField(null=True, blank=True)  # Stores LIME local weights

    def __str__(self):
        return f"Explanation for Prediction #{self.prediction.id}"

