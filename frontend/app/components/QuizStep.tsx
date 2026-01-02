"use client";

import { useState } from "react";
import { QuizData } from "../page";
import VerificationBadge from "./VerificationBadge";

interface QuizStepProps {
  quizData: QuizData;
  onSubmit: (score: number) => void;
}

export default function QuizStep({ quizData, onSubmit }: QuizStepProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: number }>({});
  const [showError, setShowError] = useState(false);

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [currentQuestion]: answerIndex,
    });
    setShowError(false);
  };

  const handleNext = () => {
    if (selectedAnswers[currentQuestion] === undefined) {
      setShowError(true);
      return;
    }

    if (currentQuestion < quizData.quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setShowError(false);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
      setShowError(false);
    }
  };

  const handleSubmit = () => {
    if (selectedAnswers[currentQuestion] === undefined) {
      setShowError(true);
      return;
    }

    // Calculate score based on weights
    let totalScore = 0;
    const maxScore = quizData.quiz.questions.length * 2; // Max weight is 2 per question

    quizData.quiz.questions.forEach((question, index) => {
      const selectedIndex = selectedAnswers[index];
      if (selectedIndex !== undefined) {
        const selectedAnswer = question.answers[selectedIndex];
        totalScore += selectedAnswer.weight;
      }
    });

    // Convert to percentage for display
    const percentageScore = Math.round((totalScore / maxScore) * 100);
    onSubmit(percentageScore);
  };

  const question = quizData.quiz.questions[currentQuestion];
  const isLastQuestion = currentQuestion === quizData.quiz.questions.length - 1;

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
      {/* Display content metadata */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <h4 className="font-bold text-gray-800 mb-2">{quizData.content.title}</h4>
        <p className="text-sm text-gray-600 mb-2">{quizData.content.description}</p>
        <div className="flex gap-2 flex-wrap">
          {quizData.content.suggested_categories.map((cat, idx) => (
            <span key={idx} className="text-xs bg-white px-2 py-1 rounded-full text-gray-700">
              {cat}
            </span>
          ))}
        </div>
      </div>

      {quizData.verification && (
        <div className="mb-6">
          <VerificationBadge verification={quizData.verification} />
        </div>
      )}

      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-3xl font-bold text-gray-800">Step 2: Take the Quiz</h2>
          <span className="text-sm font-semibold text-blue-600 bg-blue-50 px-4 py-2 rounded-full">
            Question {currentQuestion + 1} of {quizData.quiz.questions.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all"
            style={{ width: `${((currentQuestion + 1) / quizData.quiz.questions.length) * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-6">
          {question.question}
        </h3>

        <div className="space-y-3">
          {question.answers.map((answerObj, index) => (
            <button
              key={index}
              onClick={() => handleAnswerSelect(index)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                selectedAnswers[currentQuestion] === index
                  ? "border-blue-600 bg-blue-50"
                  : "border-gray-200 hover:border-blue-300 hover:bg-gray-50"
              }`}
            >
              <div className="flex items-center">
                <div
                  className={`w-6 h-6 rounded-full border-2 mr-3 flex items-center justify-center ${
                    selectedAnswers[currentQuestion] === index
                      ? "border-blue-600 bg-blue-600"
                      : "border-gray-300"
                  }`}
                >
                  {selectedAnswers[currentQuestion] === index && (
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <span className="flex-1 text-gray-800 font-medium">{answerObj.answer}</span>
              </div>
            </button>
          ))}
        </div>

        {showError && (
          <p className="mt-4 text-red-600 text-sm">Please select an answer before proceeding</p>
        )}
      </div>

      <div className="flex gap-4">
        <button
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
          className="flex-1 py-3 px-6 rounded-lg font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          Previous
        </button>
        {isLastQuestion ? (
          <button
            onClick={handleSubmit}
            className="flex-1 py-3 px-6 rounded-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg"
          >
            Submit Quiz
          </button>
        ) : (
          <button
            onClick={handleNext}
            className="flex-1 py-3 px-6 rounded-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
