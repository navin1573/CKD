import csv
import io
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from .models import Doctor, Patient, Prediction, Explanation
from .serializers import UserSerializer, DoctorSerializer, PatientSerializer, PredictionSerializer
from .ml.inference import predict_and_explain
from .pdf_generator import generate_prediction_pdf

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='5/h', method='POST'))
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": f"Registration failed: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        data = serializer.data
        
        # Add profile IDs to response for easy frontend routing
        if user.role == 'DOCTOR' and hasattr(user, 'doctor_profile'):
            data['doctor_id'] = user.doctor_profile.id
        elif user.role == 'PATIENT' and hasattr(user, 'patient_profile'):
            data['patient_id'] = user.patient_profile.id
            
        return Response(data)


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Patient.objects.all()
        # Patients can only view their own profile
        return Patient.objects.filter(user=user)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


class PredictionViewSet(viewsets.ModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            # Doctors can see all prediction history
            return Prediction.objects.all().order_by('-prediction_date')
        elif user.role == 'PATIENT':
            # Patients can only see their own prediction history
            if hasattr(user, 'patient_profile'):
                return Prediction.objects.filter(patient=user.patient_profile).order_by('-prediction_date')
        return Prediction.objects.none()

    @method_decorator(ratelimit(key='user', rate='30/m', method='POST'))
    def create(self, request):
        user = request.user
        
        # 1. Determine which patient this prediction is for
        if user.role == 'DOCTOR':
            # Doctor must supply a patient ID
            patient_id = request.data.get('patient_id')
            if not patient_id:
                return Response({"error": "Doctors must specify a patient_id."}, status=status.HTTP_400_BAD_REQUEST)
            patient = get_object_or_404(Patient, id=patient_id)
            doctor = user.doctor_profile if hasattr(user, 'doctor_profile') else None
        else:
            # Patient runs prediction on themselves
            if not hasattr(user, 'patient_profile'):
                return Response({"error": "User does not have a patient profile."}, status=status.HTTP_400_BAD_REQUEST)
            patient = user.patient_profile
            doctor = None

        # 2. Extract feature keys from request
        features = [
            'age', 'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba', 'bgr',
            'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc', 'htn',
            'dm', 'cad', 'appet', 'pe', 'ane'
        ]
        
        patient_features = {}
        for f in features:
            val = request.data.get(f)
            # Standardize empty strings or None values
            if val == '' or val is None:
                patient_features[f] = None
            else:
                patient_features[f] = val

        # 3. Call Machine Learning inference & SHAP explainers
        try:
            inference_results = predict_and_explain(patient_features)
        except Exception as e:
            return Response({"error": f"ML pipeline inference failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 4. Save Prediction instance
        predicted_class_label = 'ckd' if inference_results['prediction'] == 1 else 'notckd'
        
        prediction = Prediction.objects.create(
            patient=patient,
            doctor=doctor,
            predicted_class=predicted_class_label,
            prediction_probability=inference_results['probability'],
            risk_level=inference_results['risk_level'],
            **patient_features  # Unpack features directly into fields
        )

        # 5. Save Explanation instance
        Explanation.objects.create(
            prediction=prediction,
            shap_values_json=json.dumps(inference_results['explanations']),
            lime_explanations_json=json.dumps({
                'base_value': inference_results['base_value'],
                'probability': inference_results['probability']
            })
        )

        # Return serialized prediction
        serializer = self.get_serializer(prediction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """
        API Endpoint: GET /api/predictions/<id>/download_pdf/
        Streams a dynamically generated medical report containing XAI figures.
        """
        prediction = get_object_or_404(Prediction, id=pk)
        
        # Access control
        user = request.user
        if user.role == 'PATIENT' and prediction.patient.user != user:
            return Response({"error": "You do not have permission to view this report."}, status=status.HTTP_403_FORBIDDEN)
            
        pdf_bytes = generate_prediction_pdf(prediction)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"CKD_Report_Patient_{prediction.patient.id}_Date_{prediction.prediction_date.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def batch_predict(self, request):
        """
        API Endpoint: POST /api/predictions/batch/
        Accepts a CSV file of multiple patients, runs ML, and returns diagnostics.
        """
        user = request.user
        if user.role != 'DOCTOR':
            return Response({"error": "Only Doctors can execute batch predictions."}, status=status.HTTP_403_FORBIDDEN)
            
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST)
            
        if not file_obj.name.endswith('.csv'):
            return Response({"error": "File must be in CSV format."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse CSV file
        try:
            csv_file = io.TextIOWrapper(file_obj, encoding='utf-8')
            reader = csv.DictReader(csv_file)
        except Exception as e:
            return Response({"error": f"Failed to parse CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
        features = [
            'age', 'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba', 'bgr',
            'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc', 'htn',
            'dm', 'cad', 'appet', 'pe', 'ane'
        ]
        
        batch_results = []
        doctor = user.doctor_profile if hasattr(user, 'doctor_profile') else None

        for row_idx, row in enumerate(reader):
            # Resolve patient
            patient_username = row.get('username')
            if not patient_username:
                continue # Skip row if it doesn't specify a patient username
                
            try:
                patient_user = User.objects.get(username=patient_username, role='PATIENT')
                patient = patient_user.patient_profile
            except User.DoesNotExist:
                # Fallback: Auto-create dummy patient user for audit
                patient_user = User.objects.create(
                    username=patient_username,
                    email=f"{patient_username}@clinic-temp.com",
                    role='PATIENT',
                    first_name=row.get('first_name', patient_username),
                    last_name=row.get('last_name', '')
                )
                patient_user.set_password("TempPatient123!")
                patient_user.save()
                patient = patient_user.patient_profile
                
            # Extract features
            patient_features = {}
            for f in features:
                val = row.get(f)
                if val == '' or val is None or val == '?':
                    patient_features[f] = None
                else:
                    patient_features[f] = val

            # Run inference
            try:
                inference_results = predict_and_explain(patient_features)
                predicted_class_label = 'ckd' if inference_results['prediction'] == 1 else 'notckd'
                
                prediction = Prediction.objects.create(
                    patient=patient,
                    doctor=doctor,
                    predicted_class=predicted_class_label,
                    prediction_probability=inference_results['probability'],
                    risk_level=inference_results['risk_level'],
                    **patient_features
                )
                
                Explanation.objects.create(
                    prediction=prediction,
                    shap_values_json=json.dumps(inference_results['explanations']),
                    lime_explanations_json=json.dumps({
                        'base_value': inference_results['base_value'],
                        'probability': inference_results['probability']
                    })
                )
                
                batch_results.append({
                    'row_index': row_idx,
                    'patient_username': patient_username,
                    'predicted_class': predicted_class_label,
                    'probability': inference_results['probability'],
                    'risk_level': inference_results['risk_level']
                })
            except Exception as e:
                batch_results.append({
                    'row_index': row_idx,
                    'patient_username': patient_username,
                    'error': str(e)
                })

        return Response({"processed_rows": len(batch_results), "results": batch_results}, status=status.HTTP_200_OK)
