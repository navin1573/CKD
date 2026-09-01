from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Doctor, Patient, Prediction, Explanation
from .serializers import UserSerializer, DoctorSerializer, PatientSerializer, PredictionSerializer
import json

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model creation and role assignment"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='PATIENT'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'PATIENT')
    
    def test_user_str_representation(self):
        expected = 'testuser (PATIENT)'
        self.assertEqual(str(self.user), expected)


class DoctorModelTest(TestCase):
    """Test Doctor model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='doctor123',
            role='DOCTOR'
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            license_number='LIC12345',
            specialization='Nephrology',
            phone='1234567890'
        )
    
    def test_doctor_creation(self):
        self.assertEqual(self.doctor.license_number, 'LIC12345')
        self.assertEqual(self.doctor.specialization, 'Nephrology')
    
    def test_doctor_str_representation(self):
        expected = 'Dr. doctor (Nephrology)'
        self.assertEqual(str(self.doctor), expected)


class PatientModelTest(TestCase):
    """Test Patient model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='patient123',
            role='PATIENT'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            medical_history_summary='No prior conditions',
            phone='9876543210'
        )
    
    def test_patient_creation(self):
        self.assertEqual(self.patient.medical_history_summary, 'No prior conditions')
        self.assertEqual(self.patient.phone, '9876543210')
    
    def test_patient_str_representation(self):
        expected = 'patient'
        self.assertEqual(str(self.patient), expected)


class PredictionModelTest(TestCase):
    """Test Prediction model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='patient123',
            role='PATIENT'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            phone='9876543210'
        )
        self.prediction = Prediction.objects.create(
            patient=self.patient,
            age=50,
            bp=80,
            sg=1.02,
            al=1,
            su=0,
            rbc='normal',
            pc='normal',
            pcc='notpresent',
            ba='notpresent',
            bgr=120,
            bu=30,
            sc=1.2,
            sod=140,
            pot=4.5,
            hemo=15,
            pcv=45,
            wc=8000,
            rc=5,
            htn='no',
            dm='no',
            cad='no',
            appet='good',
            pe='no',
            ane='no',
            predicted_class='notckd',
            prediction_probability=0.15,
            risk_level='LOW'
        )
    
    def test_prediction_creation(self):
        self.assertEqual(self.prediction.patient, self.patient)
        self.assertEqual(self.prediction.predicted_class, 'notckd')
        self.assertEqual(self.prediction.risk_level, 'LOW')


class AuthenticationAPITest(APITestCase):
    """Test Authentication API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/token/'
    
    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'role': 'PATIENT'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
    
    def test_user_login(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='PATIENT'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class PredictionAPITest(APITestCase):
    """Test Prediction API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='patient123',
            role='PATIENT'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            phone='9876543210'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_prediction(self):
        data = {
            'age': 50,
            'bp': 80,
            'sg': 1.02,
            'al': 1,
            'su': 0,
            'rbc': 'normal',
            'pc': 'normal',
            'pcc': 'notpresent',
            'ba': 'notpresent',
            'bgr': 120,
            'bu': 30,
            'sc': 1.2,
            'sod': 140,
            'pot': 4.5,
            'hemo': 15,
            'pcv': 45,
            'wc': 8000,
            'rc': 5,
            'htn': 'no',
            'dm': 'no',
            'cad': 'no',
            'appet': 'good',
            'pe': 'no',
            'ane': 'no'
        }
        response = self.client.post('/api/predictions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_predictions_patient(self):
        Prediction.objects.create(
            patient=self.patient,
            age=50,
            bp=80,
            sg=1.02,
            al=1,
            su=0,
            rbc='normal',
            pc='normal',
            pcc='notpresent',
            ba='notpresent',
            bgr=120,
            bu=30,
            sc=1.2,
            sod=140,
            pot=4.5,
            hemo=15,
            pcv=45,
            wc=8000,
            rc=5,
            htn='no',
            dm='no',
            cad='no',
            appet='good',
            pe='no',
            ane='no',
            predicted_class='notckd',
            prediction_probability=0.15,
            risk_level='LOW'
        )
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_unauthorized_prediction_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/predictions/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DoctorAccessTest(APITestCase):
    """Test Doctor access control"""
    
    def setUp(self):
        self.client = APIClient()
        self.doctor_user = User.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='doctor123',
            role='DOCTOR'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            license_number='LIC12345',
            specialization='Nephrology'
        )
        
        self.patient_user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='patient123',
            role='PATIENT'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            phone='9876543210'
        )
    
    def test_doctor_can_view_all_predictions(self):
        self.client.force_authenticate(user=self.doctor_user)
        Prediction.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            age=50,
            bp=80,
            sg=1.02,
            al=1,
            su=0,
            rbc='normal',
            pc='normal',
            pcc='notpresent',
            ba='notpresent',
            bgr=120,
            bu=30,
            sc=1.2,
            sod=140,
            pot=4.5,
            hemo=15,
            pcv=45,
            wc=8000,
            rc=5,
            htn='no',
            dm='no',
            cad='no',
            appet='good',
            pe='no',
            ane='no',
            predicted_class='notckd',
            prediction_probability=0.15,
            risk_level='LOW'
        )
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_patient_cannot_view_others_predictions(self):
        self.client.force_authenticate(user=self.patient_user)
        
        # Create another patient
        other_user = User.objects.create_user(
            username='otherpatient',
            email='other@example.com',
            password='other123',
            role='PATIENT'
        )
        other_patient = Patient.objects.create(
            user=other_user,
            phone='1234567890'
        )
        
        # Create prediction for other patient
        Prediction.objects.create(
            patient=other_patient,
            age=50,
            bp=80,
            sg=1.02,
            al=1,
            su=0,
            rbc='normal',
            pc='normal',
            pcc='notpresent',
            ba='notpresent',
            bgr=120,
            bu=30,
            sc=1.2,
            sod=140,
            pot=4.5,
            hemo=15,
            pcv=45,
            wc=8000,
            rc=5,
            htn='no',
            dm='no',
            cad='no',
            appet='good',
            pe='no',
            ane='no',
            predicted_class='notckd',
            prediction_probability=0.15,
            risk_level='LOW'
        )
        
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
