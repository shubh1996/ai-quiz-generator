"use client";

import { useState } from "react";
import UploadStep from "./components/UploadStep";
import QuizStep from "./components/QuizStep";
import ResultsStep from "./components/ResultsStep";
import PointsDisplay from "./components/PointsDisplay";

export type Answer = {
  answer: string;
  weight: number; // 0 = incorrect, 1 = partially correct, 2 = correct
};

export type Question = {
  question: string;
  num_answers: number;
  answers: Answer[];
};

export type ContentMetadata = {
  title: string;
  description: string;
  media_link: string;
  duration?: number; // in minutes
  suggested_categories: string[];
  suggested_media_type: string;
  creator_name?: string;
  thumbnail_url?: string;
};

export type VerificationStatus = "verified" | "ai_verified" | "rejected" | "pending";

export type VerificationMetadata = {
  status: VerificationStatus;
  confidence_score?: number;
  platform?: string;
  rejection_reason?: string;
  verified_at: string;
  verification_method: string;
};

export type SourceInfo = {
  source_type: string;
  source_identifier: string;
  title?: string;
  duration?: number;
  transcript_length?: number;
};

export type QuizResponse = {
  success: boolean;
  job_id: string;
  content: ContentMetadata;
  quiz: {
    num_quiz_questions: number;
    questions: Question[];
  };
  verification?: VerificationMetadata;
  source_info?: SourceInfo;
  points_awarded?: number;
  generated_at: string;
};

// Legacy type for internal use
export type QuizData = QuizResponse;

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
            <ResultsStep score={score} totalQuestions={quizData.quiz.questions.length} quizData={quizData} onRestart={handleRestart} />
          )}
        </main>

        <footer className="text-center mt-16 text-gray-500 text-sm">
          <p>Powered by AI • Generate smarter quizzes instantly</p>
        </footer>
      </div>
    </div>
  );
}
