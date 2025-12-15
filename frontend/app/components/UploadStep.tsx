"use client";

import { useState } from "react";
import { QuizData } from "../page";

interface UploadStepProps {
  onQuizGenerated: (data: QuizData) => void;
}

export default function UploadStep({ onQuizGenerated }: UploadStepProps) {
  const [uploadType, setUploadType] = useState<"file" | "url">("file");
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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

    try {
      const formData = new FormData();

      if (uploadType === "file" && file) {
        formData.append("file", file);
      } else if (uploadType === "url" && url) {
        formData.append("url", url);
      } else {
        setError("Please provide a file or URL");
        setLoading(false);
        return;
      }

      const response = await fetch("http://localhost:8000/api/generate-quiz", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to generate quiz" }));
        throw new Error(errorData.detail || "Failed to generate quiz");
      }

      const data = await response.json();
      onQuizGenerated(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Step 1: Upload Content</h2>
        <p className="text-gray-600">Choose a document or paste a URL to get started</p>
      </div>

      <div className="flex gap-4 mb-8">
        <button
          onClick={() => setUploadType("file")}
          className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
            uploadType === "file"
              ? "bg-blue-600 text-white shadow-lg"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          📄 Upload File
        </button>
        <button
          onClick={() => setUploadType("url")}
          className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
            uploadType === "url"
              ? "bg-blue-600 text-white shadow-lg"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          🔗 Paste URL
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {uploadType === "file" ? (
          <div>
            <label className="block mb-2 text-sm font-medium text-gray-700">
              Choose a document (PDF, TXT, DOCX)
            </label>
            <div className="relative">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.txt,.doc,.docx"
                className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent p-3"
              />
            </div>
            {file && (
              <p className="mt-2 text-sm text-green-600">
                Selected: {file.name}
              </p>
            )}
          </div>
        ) : (
          <div>
            <label className="block mb-2 text-sm font-medium text-gray-700">
              Enter URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 font-medium placeholder-gray-400"
            />
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
  );
}
