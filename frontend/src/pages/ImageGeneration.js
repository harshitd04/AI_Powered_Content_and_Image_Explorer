import React, { useState } from 'react';
import axios from 'axios';
import { PhotoIcon, ArrowDownTrayIcon, ClockIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';

const ImageGeneration = () => {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parameters, setParameters] = useState({
    width: 512,
    height: 512,
    steps: 20,
    save_result: true
  });

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/image', {
        prompt: prompt.trim(),
        width: parameters.width,
        height: parameters.height,
        steps: parameters.steps,
        save_result: parameters.save_result
      });

      setResult(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Image generation failed. Please try again.');
      console.error('Image generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (result?.image_url) {
      const link = document.createElement('a');
      link.href = result.image_url;
      link.download = `ai-generated-${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
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

  const presetPrompts = [
    "A serene mountain landscape at sunset with a crystal clear lake",
    "A futuristic city with flying cars and neon lights",
    "An astronaut riding a unicorn on Mars",
    "A cozy coffee shop in a rainy day with warm lighting",
    "A magical forest with glowing mushrooms and fairy lights"
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI Image Generation
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Create stunning images from text descriptions using AI
        </p>
      </div>

      {/* Generation Form */}
      <div className="card p-6">
        <form onSubmit={handleGenerate} className="space-y-6">
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Image Description
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the image you want to generate..."
              rows={4}
              className="input-field resize-none"
              disabled={loading}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Be descriptive and specific for better results
            </p>
          </div>

          {/* Preset Prompts */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Try these examples:
            </label>
            <div className="flex flex-wrap gap-2">
              {presetPrompts.map((presetPrompt, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setPrompt(presetPrompt)}
                  className="text-xs px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                  disabled={loading}
                >
                  {presetPrompt.length > 50 ? `${presetPrompt.substring(0, 50)}...` : presetPrompt}
                </button>
              ))}
            </div>
          </div>

          {/* Parameters */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label htmlFor="width" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Width
              </label>
              <select
                id="width"
                value={parameters.width}
                onChange={(e) => setParameters({...parameters, width: parseInt(e.target.value)})}
                className="input-field"
                disabled={loading}
              >
                <option value={256}>256px</option>
                <option value={512}>512px</option>
                <option value={768}>768px</option>
                <option value={1024}>1024px</option>
              </select>
            </div>

            <div>
              <label htmlFor="height" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Height
              </label>
              <select
                id="height"
                value={parameters.height}
                onChange={(e) => setParameters({...parameters, height: parseInt(e.target.value)})}
                className="input-field"
                disabled={loading}
              >
                <option value={256}>256px</option>
                <option value={512}>512px</option>
                <option value={768}>768px</option>
                <option value={1024}>1024px</option>
              </select>
            </div>

            <div>
              <label htmlFor="steps" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quality Steps
              </label>
              <select
                id="steps"
                value={parameters.steps}
                onChange={(e) => setParameters({...parameters, steps: parseInt(e.target.value)})}
                className="input-field"
                disabled={loading}
              >
                <option value={10}>10 (Fast)</option>
                <option value={20}>20 (Balanced)</option>
                <option value={30}>30 (High Quality)</option>
                <option value={50}>50 (Best Quality)</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={parameters.save_result}
                onChange={(e) => setParameters({...parameters, save_result: e.target.checked})}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                disabled={loading}
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Save image to dashboard
              </span>
            </label>

            <button
              type="submit"
              disabled={loading || !prompt.trim()}
              className="btn-primary flex items-center space-x-2"
            >
              {loading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <PhotoIcon className="w-4 h-4" />
                  <span>Generate Image</span>
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

      {/* Generated Image */}
      {result && (
        <div className="card p-6 animate-slide-up">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Generated Image
            </h2>
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <ClockIcon className="w-4 h-4 mr-1" />
              {formatDate(result.timestamp)}
            </div>
          </div>

          <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <strong>Prompt:</strong> {result.prompt}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              <strong>Dimensions:</strong> {result.parameters.width} × {result.parameters.height}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              <strong>Steps:</strong> {result.parameters.steps}
            </p>
          </div>

          <div className="text-center">
            {result.image_url ? (
              <div className="space-y-4">
                <img
                  src={result.image_url}
                  alt={result.prompt}
                  className="max-w-full h-auto rounded-lg shadow-lg mx-auto"
                  style={{ maxHeight: '600px' }}
                />
                <button
                  onClick={handleDownload}
                  className="btn-secondary flex items-center space-x-2 mx-auto"
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  <span>Download Image</span>
                </button>
              </div>
            ) : result.image_data ? (
              <div className="space-y-4">
                <img
                  src={result.image_data}
                  alt={result.prompt}
                  className="max-w-full h-auto rounded-lg shadow-lg mx-auto"
                  style={{ maxHeight: '600px' }}
                />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Image generated successfully
                </p>
              </div>
            ) : (
              <div className="py-8">
                <p className="text-gray-500 dark:text-gray-400">
                  Image generation completed, but no image data received.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="card p-12">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600 dark:text-gray-400">
              Generating image from "{prompt.substring(0, 50)}{prompt.length > 50 ? '...' : ''}"
            </p>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              This may take a few moments...
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageGeneration;