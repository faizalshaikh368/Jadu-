'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface Diagnosis {
  root_cause: string;
  explanation: string;
  fix: string;
  kubectl_command: string;
  prevention: string;
  confidence: number;
}

interface InvestigationResult {
  status: string;
  investigation: {
    pods: any;
    logs: any;
    events: any;
    deployments: any;
    network: any;
  };
  diagnosis: Diagnosis;
}

interface Cluster {
  name: string;
  current: boolean;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>('');
  const [loadingClusters, setLoadingClusters] = useState(true);

  // Fetch available clusters on mount
  useEffect(() => {
    fetchClusters();
  }, []);

  const fetchClusters = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/clusters`);
      if (response.data.success) {
        const clusterList = response.data.clusters.map((name: string) => ({
          name,
          current: name === response.data.current,
        }));
        setClusters(clusterList);
        // Select current cluster by default
        if (response.data.current) {
          setSelectedCluster(response.data.current);
        } else if (clusterList.length > 0) {
          setSelectedCluster(clusterList[0].name);
        }
      }
    } catch (err) {
      console.error('Failed to fetch clusters:', err);
    } finally {
      setLoadingClusters(false);
    }
  };

  const handleInvestigate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/investigate`,
        { cluster_name: selectedCluster || undefined }
      );
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Investigation failed. Please try again.');
      console.error('Investigation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Kubernetes Agent
          </h1>
          <p className="text-xl text-gray-600">
            Troubleshoot Kubernetes with AI
          </p>
        </div>

        {/* Main CTA */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          {/* Cluster Selector */}
          <div className="mb-6">
            <label htmlFor="cluster-select" className="block text-sm font-medium text-gray-700 mb-2">
              Select Kubernetes Cluster
            </label>
            {loadingClusters ? (
              <div className="text-gray-500">Loading clusters...</div>
            ) : clusters.length > 0 ? (
              <select
                id="cluster-select"
                value={selectedCluster}
                onChange={(e) => setSelectedCluster(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {clusters.map((cluster) => (
                  <option key={cluster.name} value={cluster.name}>
                    {cluster.name} {cluster.current ? '(current)' : ''}
                  </option>
                ))}
              </select>
            ) : (
              <div className="text-yellow-600 bg-yellow-50 p-3 rounded">
                No clusters found. Please configure kubectl.
              </div>
            )}
          </div>

          {/* Investigate Button */}
          <div className="text-center">
            <button
              onClick={handleInvestigate}
              disabled={loading || clusters.length === 0}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-8 rounded-lg text-lg transition-colors"
            >
              {loading ? 'Investigating...' : 'Investigate Cluster'}
            </button>
          </div>

          {/* Status */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              System Status:{' '}
              <span className="text-green-600 font-medium">Ready</span>
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
              <p className="mt-4 text-gray-700">Investigating Kubernetes Cluster...</p>
              <p className="mt-2 text-sm text-gray-500">
                Checking pods, logs, events, deployments, and networking...
              </p>
            </div>
          </div>
        )}

        {/* Diagnosis Result */}
        {result && result.status === 'success' && (
          <div className="space-y-6">
            {/* Root Cause Card */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Diagnosis</h2>

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Root Cause</h3>
                  <p className="text-gray-700 bg-gray-50 p-4 rounded">
                    {result.diagnosis.root_cause}
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Explanation</h3>
                  <p className="text-gray-700 bg-gray-50 p-4 rounded">
                    {result.diagnosis.explanation}
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Suggested Fix</h3>
                  <p className="text-gray-700 bg-gray-50 p-4 rounded whitespace-pre-wrap">
                    {result.diagnosis.fix}
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">kubectl Command</h3>
                  <code className="block bg-gray-900 text-green-400 p-4 rounded font-mono text-sm">
                    {result.diagnosis.kubectl_command}
                  </code>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Prevention</h3>
                  <p className="text-gray-700 bg-gray-50 p-4 rounded">
                    {result.diagnosis.prevention}
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Confidence</h3>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-4 mr-4">
                      <div
                        className="bg-blue-600 h-4 rounded-full"
                        style={{ width: `${result.diagnosis.confidence}%` }}
                      ></div>
                    </div>
                    <span className="text-gray-700 font-medium">
                      {result.diagnosis.confidence}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Investigation Details */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Investigation Details</h2>
              <div className="text-sm text-gray-600 space-y-1">
                <p>Cluster: {selectedCluster || 'default'}</p>
                <p>Pods: {result.investigation.pods.total_pods} total</p>
                <p>Events: {result.investigation.events.events?.length || 0} collected</p>
                <p>Deployments: {result.investigation.deployments.deployments?.length || 0} found</p>
              </div>
            </div>
          </div>
        )}

        {/* No Issues Found */}
        {result && result.status === 'success' && result.diagnosis.confidence === 0 && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center">
              <p className="text-xl text-gray-700">No critical Kubernetes issues detected.</p>
              <p className="text-gray-600 mt-2">Cluster appears healthy.</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}