import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  MagnifyingGlassIcon, 
  PhotoIcon, 
  TrashIcon,
  CalendarIcon,
  UserIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, searches, images
  const [dateFilter, setDateFilter] = useState('all'); // all, today, week, month

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteSearch = async (searchId) => {
    try {
      await axios.delete(`/dashboard/search/${searchId}`);
      fetchDashboardData(); // Refresh data
    } catch (error) {
      console.error('Delete search error:', error);
    }
  };

  const deleteImage = async (imageId) => {
    try {
      await axios.delete(`/dashboard/image/${imageId}`);
      fetchDashboardData(); // Refresh data
    } catch (error) {
      console.error('Delete image error:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  const { stats, recent_searches, recent_images } = dashboardData;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <div className="flex items-center space-x-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input-field text-sm"
          >
            <option value="all">All Content</option>
            <option value="searches">Searches Only</option>
            <option value="images">Images Only</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <MagnifyingGlassIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Searches
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.total_searches}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {stats.searches_today} today
            </span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <PhotoIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Images
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.total_images}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {stats.images_today} today
            </span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <UserIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Member Since
              </p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {formatDate(stats.member_since).split(',')[0]}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
              <CalendarIcon className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Last Activity
              </p>
              <p className="text-sm font-bold text-gray-900 dark:text-white">
                {stats.last_activity ? formatDate(stats.last_activity) : 'No activity'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Searches */}
        {(filter === 'all' || filter === 'searches') && (
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Recent Searches
              </h2>
              <MagnifyingGlassIcon className="w-5 h-5 text-gray-400" />
            </div>
            
            <div className="space-y-4">
              {recent_searches.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No searches yet. Try searching for something!
                </p>
              ) : (
                recent_searches.map((search) => (
                  <div key={search.id} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white mb-1">
                          {search.query}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {formatDate(search.timestamp)}
                        </p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                          {search.results.length} results
                        </p>
                      </div>
                      <button
                        onClick={() => deleteSearch(search.id)}
                        className="p-1 text-gray-400 hover:text-red-500 transition-colors duration-200"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Recent Images */}
        {(filter === 'all' || filter === 'images') && (
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Recent Images
              </h2>
              <PhotoIcon className="w-5 h-5 text-gray-400" />
            </div>
            
            <div className="space-y-4">
              {recent_images.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No images generated yet. Create your first image!
                </p>
              ) : (
                recent_images.map((image) => (
                  <div key={image.id} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white mb-1">
                          {image.prompt.length > 50 ? `${image.prompt.substring(0, 50)}...` : image.prompt}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {formatDate(image.timestamp)}
                        </p>
                        {image.image_url && (
                          <img 
                            src={image.image_url} 
                            alt={image.prompt}
                            className="mt-2 w-16 h-16 object-cover rounded-lg"
                          />
                        )}
                      </div>
                      <button
                        onClick={() => deleteImage(image.id)}
                        className="p-1 text-gray-400 hover:text-red-500 transition-colors duration-200"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;