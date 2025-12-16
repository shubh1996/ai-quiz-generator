"use client";

import { useState } from "react";
import UploadStep from "./components/UploadStep";
import QuizStep from "./components/QuizStep";
import ResultsStep from "./components/ResultsStep";
import PointsDisplay from "./components/PointsDisplay";

export type Question = {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number;
};

export type VerificationStatus = "verified" | "ai_verified" | "rejected" | "pending";

export type VerificationMetadata = {
  status: VerificationStatus;
  confidenceScore?: number;
  platform?: string;
  rejectionReason?: string;
  verifiedAt: string;
  verificationMethod: string;
};

export type SourceInfo = {
  sourceType: string;
  sourceIdentifier: string;
  title?: string;
  duration?: number;
  transcriptLength?: number;
};

export type QuizData = {
  questions: Question[];
  verification?: VerificationMetadata;
  sourceInfo?: SourceInfo;
  pointsAwarded?: number;
};

export default function Home() {
  const [currentStep, setCurrentStep] = useState<"upload" | "quiz" | "results">("upload");
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [score, setScore] = useState<number>(0);

  const handleQuizGenerated = (data: QuizData) => {
    setQuizData(data);
    setCurrentStep("quiz");
  };

  const handleQuizSubmit = (userScore: number) => {
    setScore(userScore);
    setCurrentStep("results");
  };

  const handleRestart = () => {
    setCurrentStep("upload");
    setQuizData(null);
    setScore(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <PointsDisplay />
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            AI Quiz Generator
          </h1>
          <p className="text-gray-600 text-lg">
            Upload a document, URL, or video to generate an intelligent quiz
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          {currentStep === "upload" && (
            <UploadStep onQuizGenerated={handleQuizGenerated} />
          )}
          {currentStep === "quiz" && quizData && (
            <QuizStep quizData={quizData} onSubmit={handleQuizSubmit} />
          )}
          {currentStep === "results" && quizData && (
            <ResultsStep score={score} totalQuestions={quizData.questions.length} quizData={quizData} onRestart={handleRestart} />
          )}
        </main>

        <footer className="text-center mt-16 text-gray-500 text-sm">
          <p>Powered by AI • Generate smarter quizzes instantly</p>
        </footer>
      </div>
    </div>
  );
}
