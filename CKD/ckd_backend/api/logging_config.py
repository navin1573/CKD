import logging
import os
from datetime import datetime

def setup_logging():
    """
    Configure logging for the Django application.
    Creates log files for different components and sets up formatting.
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Define log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'django.log')),
            logging.StreamHandler()
        ]
    )

    # Create separate loggers for different components
    loggers = {
        'api': os.path.join(log_dir, 'api.log'),
        'ml': os.path.join(log_dir, 'ml.log'),
        'auth': os.path.join(log_dir, 'auth.log'),
        'predictions': os.path.join(log_dir, 'predictions.log')
    }

    for logger_name, log_file in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logging.getLogger(__name__)


class APILogger:
    """Custom logger for API requests and responses"""
    
    def __init__(self):
        self.logger = logging.getLogger('api')
    
    def log_request(self, request):
        """Log incoming API request"""
        self.logger.info(
            f"Request: {request.method} {request.path} - "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'} - "
            f"IP: {self.get_client_ip(request)}"
        )
    
    def log_response(self, response, request):
        """Log API response"""
        self.logger.info(
            f"Response: {request.method} {request.path} - "
            f"Status: {response.status_code} - "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
        )
    
    def log_error(self, error, request=None):
        """Log API error"""
        if request:
            self.logger.error(
                f"Error: {request.method} {request.path} - "
                f"Error: {str(error)} - "
                f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
            )
        else:
            self.logger.error(f"Error: {str(error)}")
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MLLogger:
    """Custom logger for ML operations"""
    
    def __init__(self):
        self.logger = logging.getLogger('ml')
    
    def log_prediction(self, patient_id, prediction_result, processing_time):
        """Log ML prediction"""
        self.logger.info(
            f"Prediction - Patient: {patient_id} - "
            f"Result: {prediction_result.get('predicted_class')} - "
            f"Probability: {prediction_result.get('probability'):.4f} - "
            f"Processing Time: {processing_time:.2f}s"
        )
    
    def log_model_load(self, model_name):
        """Log model loading"""
        self.logger.info(f"Model loaded: {model_name}")
    
    def log_model_error(self, error, context):
        """Log ML model error"""
        self.logger.error(f"ML Error - Context: {context} - Error: {str(error)}")


class AuthLogger:
    """Custom logger for authentication operations"""
    
    def __init__(self):
        self.logger = logging.getLogger('auth')
    
    def log_login(self, username, success=True):
        """Log user login attempt"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Login {status} - Username: {username}")
    
    def log_registration(self, username, email, role):
        """Log user registration"""
        self.logger.info(
            f"Registration - Username: {username} - "
            f"Email: {email} - Role: {role}"
        )
    
    def log_logout(self, username):
        """Log user logout"""
        self.logger.info(f"Logout - Username: {username}")


class PredictionLogger:
    """Custom logger for prediction operations"""
    
    def __init__(self):
        self.logger = logging.getLogger('predictions')
    
    def log_prediction_created(self, prediction_id, patient_id, risk_level):
        """Log prediction creation"""
        self.logger.info(
            f"Prediction Created - ID: {prediction_id} - "
            f"Patient: {patient_id} - Risk Level: {risk_level}"
        )
    
    def log_batch_prediction(self, doctor_id, total_rows, successful_rows):
        """Log batch prediction operation"""
        self.logger.info(
            f"Batch Prediction - Doctor: {doctor_id} - "
            f"Total: {total_rows} - Successful: {successful_rows}"
        )
    
    def log_pdf_generation(self, prediction_id, success=True):
        """Log PDF report generation"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"PDF Generation {status} - Prediction ID: {prediction_id}")
