"use client";

import { useState, useEffect } from 'react';
import { AvatarScene } from '../components/avatar/AvatarScene';

export default function Home() {
  const [topic, setTopic] = useState('');
  const [emotion, setEmotion] = useState('neutral');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse(null);
    setIsSpeaking(false);

    try {
      const res = await fetch('http://localhost:8000/api/v1/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, emotion }),
      });

      const data = await res.json();
      setResponse(data);

      // Simulate speaking for a duration based on script length
      setIsSpeaking(true);
      const speakingDurationMs = data.script.length * 50; // roughly 50ms per character
      setTimeout(() => setIsSpeaking(false), speakingDurationMs);

    } catch (error) {
      console.error("Error generating content:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

      {/* Sidebar Controls */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold mb-6">Configure Avatar</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="topic" className="block text-sm font-medium text-gray-700">
              What should the avatar explain?
            </label>
            <textarea
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
              placeholder="e.g. How quantum computing works"
              rows={4}
              required
            />
          </div>

          <div>
            <label htmlFor="emotion" className="block text-sm font-medium text-gray-700">
              Select Emotion Preset
            </label>
            <select
              id="emotion"
              value={emotion}
              onChange={(e) => setEmotion(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            >
              <option value="neutral">Neutral (Balanced)</option>
              <option value="excited">Excited (High Energy)</option>
              <option value="heartbroken">Heartbroken (Sad & Slow)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading || !topic}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Explainer'}
          </button>
        </form>
      </div>

      {/* Main Avatar Stage & Outputs */}
      <div className="lg:col-span-2 space-y-6">

        {/* 3D Stage */}
        <div className="bg-black w-full h-[500px] rounded-lg shadow-inner overflow-hidden relative">
          {response ? (
             <AvatarScene emotionConfig={response.emotion_mapping} isSpeaking={isSpeaking} />
          ) : (
             <AvatarScene emotionConfig={{ animation: { color_overlay: "#333333" } }} isSpeaking={false} />
          )}
        </div>

        {/* Script & Details */}
        {response && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Generated Output</h3>

            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Script</h4>
              <p className="mt-2 text-gray-800 text-lg italic border-l-4 border-indigo-500 pl-4">
                "{response.script}"
              </p>
            </div>

            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Mock Audio URL</h4>
              <p className="mt-1 text-sm text-blue-600 break-all">{response.audio_url}</p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Applied Emotion Config</h4>
              <pre className="mt-2 bg-gray-100 p-4 rounded text-xs overflow-auto max-h-48">
                {JSON.stringify(response.emotion_mapping, null, 2)}
              </pre>
            </div>

          </div>
        )}

      </div>

    </div>
  );
}
