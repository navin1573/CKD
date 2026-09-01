import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

const SHAPVisualization = ({ explanationData, predictionData }) => {
  const [shapData, setShapData] = useState(null);

  useEffect(() => {
    if (explanationData && explanationData.shap_values_json) {
      try {
        const shapValues = JSON.parse(explanationData.shap_values_json);
        setShapData(shapValues);
      } catch (error) {
        console.error('Error parsing SHAP data:', error);
      }
    }
  }, [explanationData]);

  if (!shapData) {
    return (
      <div className="bg-gray-100 rounded-lg p-6 text-center">
        <p className="text-gray-500">No SHAP explanation data available</p>
      </div>
    );
  }

  // Prepare data for feature importance bar chart
  const featureNames = Object.keys(shapData);
  const featureValues = Object.values(shapData).map(Math.abs);

  const barChartData = [{
    type: 'bar',
    x: featureValues,
    y: featureNames,
    orientation: 'h',
    marker: {
      color: featureValues,
      colorscale: 'RdYlGn',
      reversescale: true
    }
  }];

  const barChartLayout = {
    title: 'Feature Importance (SHAP Values)',
    xaxis: { title: 'Absolute SHAP Value' },
    yaxis: { title: 'Features' },
    margin: { l: 150, r: 50, t: 50, b: 50 },
    height: 400
  };

  // Prepare data for waterfall chart (positive/negative contributions)
  const positiveContributions = {};
  const negativeContributions = {};

  Object.entries(shapData).forEach(([feature, value]) => {
    if (value >= 0) {
      positiveContributions[feature] = value;
    } else {
      negativeContributions[feature] = value;
    }
  });

  const waterfallData = [{
    type: 'waterfall',
    orientation: 'v',
    x: [...Object.keys(negativeContributions), 'Base', ...Object.keys(positiveContributions)],
    y: [...Object.values(negativeContributions), 0, ...Object.values(positiveContributions)],
    text: [...Object.values(negativeContributions).map(v => v.toFixed(3)), 
           '0', 
           ...Object.values(positiveContributions).map(v => `+${v.toFixed(3)}`)],
    textposition: 'outside',
    decreasing: { marker: { color: 'red' } },
    increasing: { marker: { color: 'green' } },
    totals: { marker: { color: 'blue' } }
  }];

  const waterfallLayout = {
    title: 'SHAP Value Contributions',
    xaxis: { title: 'Features' },
    yaxis: { title: 'Contribution to Prediction' },
    margin: { l: 50, r: 50, t: 50, b: 150 },
    height: 400
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800">Feature Importance</h3>
        <Plot
          data={barChartData}
          layout={barChartLayout}
          config={{ responsive: true, displayModeBar: true }}
          className="w-full"
        />
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800">Feature Contributions</h3>
        <Plot
          data={waterfallData}
          layout={waterfallLayout}
          config={{ responsive: true, displayModeBar: true }}
          className="w-full"
        />
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800">Detailed SHAP Analysis</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Feature
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SHAP Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Impact
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(shapData).map(([feature, value]) => (
                <tr key={feature}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {feature}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {value.toFixed(4)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      value > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {value > 0 ? 'Increases Risk' : 'Decreases Risk'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SHAPVisualization;
