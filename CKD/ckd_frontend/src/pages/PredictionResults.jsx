import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { predictionAPI } from '../services/api';
import { Download, ArrowLeft, AlertTriangle, CheckCircle, Activity } from 'lucide-react';

const PredictionResults = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    loadPrediction();
  }, [id]);

  const loadPrediction = async () => {
    try {
      const response = await predictionAPI.get(id);
      setPrediction(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load prediction:', error);
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const response = await predictionAPI.downloadPDF(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `CKD_Report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setDownloading(false);
    } catch (error) {
      console.error('Failed to download PDF:', error);
      setDownloading(false);
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRiskIcon = (level) => {
    switch (level) {
      case 'high': return <AlertTriangle className="h-6 w-6 text-red-600" />;
      case 'medium': return <AlertTriangle className="h-6 w-6 text-yellow-600" />;
      case 'low': return <CheckCircle className="h-6 w-6 text-green-600" />;
      default: return <Activity className="h-6 w-6 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="text-center py-12">Loading prediction results...</div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="text-center py-12">Prediction not found</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Back</span>
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Prediction Results</h1>
        <p className="mt-2 text-gray-600">
          Prediction ID: {prediction.id} • {new Date(prediction.prediction_date).toLocaleString()}
        </p>
      </div>

      {/* Main Result Card */}
      <div className={`card border-2 ${getRiskLevelColor(prediction.risk_level)} mb-6`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {getRiskIcon(prediction.risk_level)}
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {prediction.predicted_class === 'ckd' ? 'CKD Detected' : 'No CKD Detected'}
              </h2>
              <p className="text-gray-600 mt-1">
                Probability: {(prediction.prediction_probability * 100).toFixed(1)}%
              </p>
            </div>
          </div>
          <div className="text-right">
            <span className={`inline-block px-4 py-2 rounded-full text-lg font-bold ${getRiskLevelColor(prediction.risk_level)}`}>
              {prediction.risk_level.toUpperCase()} RISK
            </span>
          </div>
        </div>
      </div>

      {/* Clinical Parameters */}
      <div className="card mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Clinical Parameters</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Age</p>
            <p className="text-lg font-semibold">{prediction.age}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Blood Pressure</p>
            <p className="text-lg font-semibold">{prediction.bp}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Specific Gravity</p>
            <p className="text-lg font-semibold">{prediction.sg}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Albumin</p>
            <p className="text-lg font-semibold">{prediction.al}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Sugar</p>
            <p className="text-lg font-semibold">{prediction.su}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Blood Glucose</p>
            <p className="text-lg font-semibold">{prediction.bgr}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Blood Urea</p>
            <p className="text-lg font-semibold">{prediction.bu}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Serum Creatinine</p>
            <p className="text-lg font-semibold">{prediction.sc}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Sodium</p>
            <p className="text-lg font-semibold">{prediction.sod}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Potassium</p>
            <p className="text-lg font-semibold">{prediction.pot}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">Hemoglobin</p>
            <p className="text-lg font-semibold">{prediction.hemo}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-500">PCV</p>
            <p className="text-lg font-semibold">{prediction.pcv}</p>
          </div>
        </div>
      </div>

      {/* Additional Parameters */}
      <div className="card mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Additional Parameters</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">RBC:</span>
            <span className="font-semibold">{prediction.rbc}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">PC:</span>
            <span className="font-semibold">{prediction.pc}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">PCC:</span>
            <span className="font-semibold">{prediction.pcc}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">BA:</span>
            <span className="font-semibold">{prediction.ba}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">HTN:</span>
            <span className="font-semibold">{prediction.htn}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">DM:</span>
            <span className="font-semibold">{prediction.dm}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">CAD:</span>
            <span className="font-semibold">{prediction.cad}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">Appetite:</span>
            <span className="font-semibold">{prediction.appet}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">Pedal Edema:</span>
            <span className="font-semibold">{prediction.pe}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">Anemia:</span>
            <span className="font-semibold">{prediction.ane}</span>
          </div>
        </div>
      </div>

      {/* Download PDF Button */}
      <div className="flex justify-end">
        <button
          onClick={handleDownloadPDF}
          disabled={downloading}
          className="btn-primary flex items-center space-x-2"
        >
          <Download className="h-5 w-5" />
          <span>{downloading ? 'Downloading...' : 'Download PDF Report'}</span>
        </button>
      </div>
    </div>
  );
};

export default PredictionResults;
