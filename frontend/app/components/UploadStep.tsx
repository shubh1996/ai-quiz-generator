"use client";

import { useState } from "react";
import { QuizData } from "../page";
import RejectionModal from "./RejectionModal";

interface UploadStepProps {
  onQuizGenerated: (data: QuizData) => void;
}

export default function UploadStep({ onQuizGenerated }: UploadStepProps) {
  const [uploadType, setUploadType] = useState<"file" | "url" | "video">("file");
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showRejectionModal, setShowRejectionModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");
  const [rejectionConfidence, setRejectionConfidence] = useState<number | undefined>();
  const [ageMode, setAgeMode] = useState<"kids" | "18+">("18+"); // Content safety mode

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    try {
      const formData = new FormData();

      if (uploadType === "file" && file) {
        formData.append("file", file);
      } else if (uploadType === "url" && url) {
        formData.append("url", url);
      } else if (uploadType === "video" && videoUrl) {
        formData.append("video_url", videoUrl);
      } else {
        setError("Please provide a file, URL, or video URL");
        setLoading(false);
        return;
      }

      // Add age mode for content safety filtering
      formData.append("age_mode", ageMode);

      // Add timeout to prevent hanging requests (2 minutes for video/document processing)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

      try {
        const response = await fetch(`${apiUrl}/api/generate-quiz`, {
          method: "POST",
          body: formData,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to generate quiz" }));

        // Handle rejection (403)
        if (response.status === 403 && errorData.detail) {
          setRejectionReason(errorData.detail.reason || errorData.detail);
          setRejectionConfidence(errorData.detail.confidence);
          setShowRejectionModal(true);
          setLoading(false);
          return;
        }

        throw new Error(errorData.detail || "Failed to generate quiz");
      }

        const data = await response.json();
        onQuizGenerated(data);
      } catch (fetchErr) {
        clearTimeout(timeoutId);
        if (fetchErr instanceof Error && fetchErr.name === 'AbortError') {
          throw new Error("Request timed out. The document/video may be too large or the server is taking too long to process.");
        }
        throw fetchErr;
      }
    } catch (err) {
      console.error('Quiz generation error:', err);

      // Provide helpful error messages
      if (err instanceof Error) {
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          setError(`Cannot connect to server. Please check:\n1. Backend URL is configured correctly\n2. Server is running\n3. Internet connection is active\n\nAPI URL: ${apiUrl}`);
        } else {
          setError(err.message);
        }
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <RejectionModal
        isOpen={showRejectionModal}
        onClose={() => setShowRejectionModal(false)}
        reason={rejectionReason}
        confidence={rejectionConfidence}
      />

      <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">Step 1: Upload Content</h2>
          <p className="text-gray-600">Choose a document, URL, or video to get started</p>
        </div>

        {/* Age Mode Toggle - CRITICAL for content safety */}
        <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="font-bold text-gray-800 flex items-center gap-2">
                🛡️ Content Safety Mode
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {ageMode === "kids"
                  ? "Kid-safe mode: Blocks violence, substances, mature themes, and inappropriate content"
                  : "Adult mode: Basic filtering for extremely inappropriate content only"}
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setAgeMode("kids")}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all ${
                ageMode === "kids"
                  ? "bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg"
                  : "bg-white text-gray-600 border-2 border-gray-300 hover:border-green-400"
              }`}
            >
              👶 Under 18 (Kid-Safe)
            </button>
            <button
              type="button"
              onClick={() => setAgeMode("18+")}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all ${
                ageMode === "18+"
                  ? "bg-gradient-to-r from-purple-500 to-violet-500 text-white shadow-lg"
                  : "bg-white text-gray-600 border-2 border-gray-300 hover:border-purple-400"
              }`}
            >
              🎓 18+ (Adult)
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <button
            onClick={() => setUploadType("file")}
            className={`py-3 px-4 rounded-lg font-semibold transition-all ${
              uploadType === "file"
                ? "bg-blue-600 text-white shadow-lg"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            📄 Upload File
          </button>
          <button
            onClick={() => setUploadType("url")}
            className={`py-3 px-4 rounded-lg font-semibold transition-all ${
              uploadType === "url"
                ? "bg-blue-600 text-white shadow-lg"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            🔗 Web URL
          </button>
          <button
            onClick={() => setUploadType("video")}
            className={`py-3 px-4 rounded-lg font-semibold transition-all ${
              uploadType === "video"
                ? "bg-blue-600 text-white shadow-lg"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            🎥 Video URL
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {uploadType === "file" ? (
            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Choose a document or video file
              </label>
              <div className="relative">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.txt,.doc,.docx,.mp4,.avi,.mov,.mkv,.webm"
                  className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent p-3"
                />
              </div>
              {file && (
                <p className="mt-2 text-sm text-green-600">
                  Selected: {file.name}
                </p>
              )}
              <p className="mt-2 text-xs text-gray-500">
                Supported: PDF, TXT, DOCX, MP4, AVI, MOV, MKV, WEBM
              </p>
            </div>
          ) : uploadType === "url" ? (
            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Enter Web URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/article"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 font-medium placeholder-gray-400"
              />
            </div>
          ) : (
            <div>
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Enter Video URL
              </label>
              <input
                type="url"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://youtube.com/watch?v=..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 font-medium placeholder-gray-400"
              />
              <p className="mt-2 text-xs text-gray-500">
                Supports YouTube, Vimeo, and most video platforms
              </p>
            </div>
          )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-4 px-6 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Quiz...
            </span>
          ) : (
            "Generate Quiz"
          )}
        </button>
        </form>
      </div>
    </>
  );
}
