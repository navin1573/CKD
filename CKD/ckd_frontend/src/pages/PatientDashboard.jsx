import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictionAPI } from '../services/api';
import { Heart, Plus, FileText, Calendar } from 'lucide-react';

const PatientDashboard = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadPredictions();
  }, []);

  const loadPredictions = async () => {
    try {
      const response = await predictionAPI.list();
      // Handle paginated response or direct array
      const predictionsData = Array.isArray(response.data) 
        ? response.data 
        : (response.data.results || []);
      setPredictions(predictionsData);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load predictions:', error);
      setPredictions([]);
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Patient Dashboard</h1>
          <p className="mt-2 text-gray-600">View your prediction history</p>
        </div>
        <button
          onClick={() => navigate('/predict')}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>New Prediction</span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : predictions.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Heart className="mx-auto h-16 w-16 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No predictions yet</h3>
          <p className="mt-2 text-gray-500">Start by making your first prediction</p>
          <button
            onClick={() => navigate('/predict')}
            className="mt-4 btn-primary"
          >
            Make Prediction
          </button>
        </div>
      ) : (
        <div className="grid gap-6">
          {predictions.map((prediction) => (
            <div key={prediction.id} className="card">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-5 w-5 text-gray-500" />
                    <span className="text-sm text-gray-600">
                      {new Date(prediction.prediction_date).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Prediction</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {prediction.predicted_class === 'ckd' ? 'CKD Detected' : 'No CKD'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Probability</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {(prediction.prediction_probability * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Risk Level</p>
                      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(prediction.risk_level)}`}>
                        {prediction.risk_level}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Age</p>
                      <p className="text-lg font-semibold text-gray-900">{prediction.age}</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigate(`/results/${prediction.id}`)}
                    className="btn-secondary flex items-center space-x-1"
                  >
                    <FileText className="h-4 w-4" />
                    <span>Details</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PatientDashboard;
