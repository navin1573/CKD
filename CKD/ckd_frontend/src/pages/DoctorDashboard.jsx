import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictionAPI, patientAPI } from '../services/api';
import { Users, Activity, FileText, Calendar, TrendingUp } from 'lucide-react';

const DoctorDashboard = () => {
  const [predictions, setPredictions] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('predictions');
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [predictionsRes, patientsRes] = await Promise.all([
        predictionAPI.list(),
        patientAPI.list(),
      ]);
      // Handle paginated responses
      const predictionsData = Array.isArray(predictionsRes.data) 
        ? predictionsRes.data 
        : (predictionsRes.data.results || []);
      const patientsData = Array.isArray(patientsRes.data) 
        ? patientsRes.data 
        : (patientsRes.data.results || []);
      setPredictions(predictionsData);
      setPatients(patientsData);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load data:', error);
      setPredictions([]);
      setPatients([]);
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

  const getStats = () => {
    const total = predictions.length;
    const ckd = predictions.filter(p => p.predicted_class === 'ckd').length;
    const highRisk = predictions.filter(p => p.risk_level === 'high').length;
    return { total, ckd, highRisk };
  };

  const stats = getStats();

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Doctor Dashboard</h1>
        <p className="mt-2 text-gray-600">Manage patients and view predictions</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Predictions</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <Activity className="h-8 w-8 text-primary-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">CKD Cases</p>
              <p className="text-2xl font-bold text-red-600">{stats.ckd}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">High Risk</p>
              <p className="text-2xl font-bold text-orange-600">{stats.highRisk}</p>
            </div>
            <Activity className="h-8 w-8 text-orange-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Patients</p>
              <p className="text-2xl font-bold text-gray-900">{patients.length}</p>
            </div>
            <Users className="h-8 w-8 text-primary-600" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('predictions')}
              className={`${
                activeTab === 'predictions'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Predictions
            </button>
            <button
              onClick={() => setActiveTab('patients')}
              className={`${
                activeTab === 'patients'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Patients
            </button>
          </nav>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : activeTab === 'predictions' ? (
        <div className="grid gap-4">
          {predictions.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500">No predictions yet</p>
            </div>
          ) : (
            predictions.map((prediction) => (
              <div key={prediction.id} className="card">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <Calendar className="h-5 w-5 text-gray-500" />
                      <span className="text-sm text-gray-600">
                        {new Date(prediction.prediction_date).toLocaleString()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Patient</p>
                        <p className="font-semibold text-gray-900">
                          {prediction.patient_name || `Patient #${prediction.patient}`}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Prediction</p>
                        <p className={`font-semibold ${prediction.predicted_class === 'ckd' ? 'text-red-600' : 'text-green-600'}`}>
                          {prediction.predicted_class === 'ckd' ? 'CKD Detected' : 'No CKD'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Probability</p>
                        <p className="font-semibold text-gray-900">
                          {(prediction.prediction_probability * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Risk Level</p>
                        <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(prediction.risk_level)}`}>
                          {prediction.risk_level}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => navigate(`/results/${prediction.id}`)}
                    className="btn-secondary flex items-center space-x-1 ml-4"
                  >
                    <FileText className="h-4 w-4" />
                    <span>View</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="grid gap-4">
          {patients.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500">No patients registered</p>
            </div>
          ) : (
            patients.map((patient) => (
              <div key={patient.id} className="card">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-gray-900">
                      {patient.user?.first_name} {patient.user?.last_name}
                    </p>
                    <p className="text-sm text-gray-600">{patient.user?.email}</p>
                    <p className="text-sm text-gray-500 mt-1">DOB: {patient.date_of_birth}</p>
                  </div>
                  <button
                    onClick={() => navigate(`/predict?patient_id=${patient.id}`)}
                    className="btn-primary"
                  >
                    New Prediction
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default DoctorDashboard;
