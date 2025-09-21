import React, { useState } from 'react';
import axios from 'axios';
import { MagnifyingGlassIcon, LinkIcon, ClockIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [saveResult, setSaveResult] = useState(true);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post('/search', {
        query: query.trim(),
        max_results: maxResults,
        save_result: saveResult
      });

      setResults(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Search failed. Please try again.');
      console.error('Search error:', error);
    } finally {
      setLoading(false);
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

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI-Powered Search
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Search the web with intelligent AI assistance
        </p>
      </div>

      {/* Search Form */}
      <div className="card p-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search Query
              </label>
              <div className="relative">
                <input
                  id="query"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="What would you like to search for?"
                  className="input-field pl-10"
                  disabled={loading}
                />
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>
            
            <div className="sm:w-32">
              <label htmlFor="maxResults" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Results
              </label>
              <select
                id="maxResults"
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                className="input-field"
                disabled={loading}
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={saveResult}
                onChange={(e) => setSaveResult(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                disabled={loading}
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Save search results to dashboard
              </span>
            </label>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="btn-primary flex items-center space-x-2"
            >
              {loading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <MagnifyingGlassIcon className="w-4 h-4" />
                  <span>Search</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Search Results */}
      {results && (
        <div className="card p-6 animate-slide-up">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Search Results
            </h2>
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <ClockIcon className="w-4 h-4 mr-1" />
              {formatDate(results.timestamp)}
            </div>
          </div>

          <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <strong>Query:</strong> {results.query}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              <strong>Results found:</strong> {results.results.length}
            </p>
          </div>

          <div className="space-y-4">
            {results.results.map((result, index) => (
              <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                      {result.title || `Result ${index + 1}`}
                    </h3>
                    
                    {result.snippet && (
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                        {result.snippet}
                      </p>
                    )}
                    
                    {result.content && (
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                        {result.content}
                      </p>
                    )}
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                      {result.url && (
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-200"
                        >
                          <LinkIcon className="w-3 h-3 mr-1" />
                          Visit source
                        </a>
                      )}
                      {result.source && (
                        <span className="flex items-center">
                          <span className="w-2 h-2 bg-gray-400 rounded-full mr-1"></span>
                          {result.source}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {results.results.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">
                No results found for your search query.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="card p-12">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600 dark:text-gray-400">
              Searching the web for "{query}"...
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;