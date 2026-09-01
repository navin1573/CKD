import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictionAPI } from '../services/api';
import { Heart, Activity } from 'lucide-react';

const PredictionForm = () => {
  const [formData, setFormData] = useState({
    age: '',
    bp: '',
    sg: '',
    al: '',
    su: '',
    rbc: 'normal',
    pc: 'normal',
    pcc: 'notpresent',
    ba: 'notpresent',
    bgr: '',
    bu: '',
    sc: '',
    sod: '',
    pot: '',
    hemo: '',
    pcv: '',
    wc: '',
    rc: '',
    htn: 'no',
    dm: 'no',
    cad: 'no',
    appet: 'good',
    pe: 'no',
    ane: 'no',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await predictionAPI.create(formData);
      setLoading(false);
      navigate(`/results/${response.data.id}`);
    } catch (err) {
      setError('Failed to create prediction. Please check your inputs.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Activity className="h-8 w-8 mr-3 text-primary-600" />
          CKD Prediction
        </h1>
        <p className="mt-2 text-gray-600">Enter your clinical parameters for prediction</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Numerical Fields */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Age</label>
            <input
              type="number"
              name="age"
              required
              className="input-field mt-1"
              value={formData.age}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Blood Pressure (bp)</label>
            <input
              type="number"
              name="bp"
              required
              className="input-field mt-1"
              value={formData.bp}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Specific Gravity (sg)</label>
            <input
              type="number"
              step="0.001"
              name="sg"
              required
              className="input-field mt-1"
              value={formData.sg}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Albumin (al)</label>
            <input
              type="number"
              step="0.1"
              name="al"
              required
              className="input-field mt-1"
              value={formData.al}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Sugar (su)</label>
            <input
              type="number"
              step="0.1"
              name="su"
              required
              className="input-field mt-1"
              value={formData.su}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Blood Glucose Random (bgr)</label>
            <input
              type="number"
              name="bgr"
              required
              className="input-field mt-1"
              value={formData.bgr}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Blood Urea (bu)</label>
            <input
              type="number"
              name="bu"
              required
              className="input-field mt-1"
              value={formData.bu}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Serum Creatinine (sc)</label>
            <input
              type="number"
              step="0.1"
              name="sc"
              required
              className="input-field mt-1"
              value={formData.sc}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Sodium (sod)</label>
            <input
              type="number"
              name="sod"
              required
              className="input-field mt-1"
              value={formData.sod}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Potassium (pot)</label>
            <input
              type="number"
              step="0.1"
              name="pot"
              required
              className="input-field mt-1"
              value={formData.pot}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Hemoglobin (hemo)</label>
            <input
              type="number"
              step="0.1"
              name="hemo"
              required
              className="input-field mt-1"
              value={formData.hemo}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Packed Cell Volume (pcv)</label>
            <input
              type="number"
              name="pcv"
              required
              className="input-field mt-1"
              value={formData.pcv}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">White Blood Cell Count (wc)</label>
            <input
              type="number"
              name="wc"
              required
              className="input-field mt-1"
              value={formData.wc}
              onChange={handleChange}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Red Blood Cell Count (rc)</label>
            <input
              type="number"
              step="0.01"
              name="rc"
              required
              className="input-field mt-1"
              value={formData.rc}
              onChange={handleChange}
            />
          </div>

          {/* Categorical Fields */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Red Blood Cells (rbc)</label>
            <select name="rbc" className="input-field mt-1" value={formData.rbc} onChange={handleChange}>
              <option value="normal">Normal</option>
              <option value="abnormal">Abnormal</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Pus Cell (pc)</label>
            <select name="pc" className="input-field mt-1" value={formData.pc} onChange={handleChange}>
              <option value="normal">Normal</option>
              <option value="abnormal">Abnormal</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Pus Cell Clumps (pcc)</label>
            <select name="pcc" className="input-field mt-1" value={formData.pcc} onChange={handleChange}>
              <option value="notpresent">Not Present</option>
              <option value="present">Present</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Bacteria (ba)</label>
            <select name="ba" className="input-field mt-1" value={formData.ba} onChange={handleChange}>
              <option value="notpresent">Not Present</option>
              <option value="present">Present</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Hypertension (htn)</label>
            <select name="htn" className="input-field mt-1" value={formData.htn} onChange={handleChange}>
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Diabetes Mellitus (dm)</label>
            <select name="dm" className="input-field mt-1" value={formData.dm} onChange={handleChange}>
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Coronary Artery Disease (cad)</label>
            <select name="cad" className="input-field mt-1" value={formData.cad} onChange={handleChange}>
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Appetite (appet)</label>
            <select name="appet" className="input-field mt-1" value={formData.appet} onChange={handleChange}>
              <option value="good">Good</option>
              <option value="poor">Poor</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Pedal Edema (pe)</label>
            <select name="pe" className="input-field mt-1" value={formData.pe} onChange={handleChange}>
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Anemia (ane)</label>
            <select name="ane" className="input-field mt-1" value={formData.ane} onChange={handleChange}>
              <option value="no">No</option>
              <option value="yes">Yes</option>
            </select>
          </div>
        </div>

        <div className="mt-8 flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center space-x-2"
          >
            <Heart className="h-5 w-5" />
            <span>{loading ? 'Analyzing...' : 'Get Prediction'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default PredictionForm;
