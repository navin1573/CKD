from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Doctor, Patient, Prediction, Explanation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'first_name', 'last_name', 'token')

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        return value

    def get_token(self, obj):
        # We can optionally generate SimpleJWT tokens directly upon registration
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(obj)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        except ImportError:
            return None

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', 'PATIENT')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Automatically create corresponding role profile
        if role == 'DOCTOR':
            # Create a default doctor profile, doctor can edit it later
            Doctor.objects.create(
                user=user,
                license_number=f"DOC-{user.id:04d}",
                specialization="Nephrologist"
            )
        elif role == 'PATIENT':
            # Create a default patient profile
            Patient.objects.create(user=user)
            
        return user


class DoctorSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Doctor
        fields = ('id', 'user', 'user_details', 'license_number', 'specialization', 'phone')
        read_only_fields = ('user',)


class PatientSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Patient
        fields = ('id', 'user', 'user_details', 'medical_history_summary', 'phone', 'date_of_birth')
        read_only_fields = ('user',)


class ExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Explanation
        fields = ('id', 'prediction', 'shap_values_json', 'lime_explanations_json')


class PredictionSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField(read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)
    explanation = ExplanationSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = '__all__'
        read_only_fields = ('predicted_class', 'prediction_probability', 'risk_level', 'doctor')

    def validate_age(self, value):
        """Validate age is within reasonable range"""
        if value is not None and (value < 0 or value > 120):
            raise serializers.ValidationError("Age must be between 0 and 120.")
        return value

    def validate_bp(self, value):
        """Validate blood pressure is within reasonable range"""
        if value is not None and (value < 50 or value > 250):
            raise serializers.ValidationError("Blood pressure must be between 50 and 250.")
        return value

    def validate_sg(self, value):
        """Validate specific gravity is within normal range"""
        if value is not None and (value < 1.0 or value > 1.05):
            raise serializers.ValidationError("Specific gravity must be between 1.0 and 1.05.")
        return value

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}".strip() or obj.patient.user.username

    def get_doctor_name(self, obj):
        if obj.doctor:
            return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}".strip() or f"Dr. {obj.doctor.user.username}"
        return "Self Prediction"
