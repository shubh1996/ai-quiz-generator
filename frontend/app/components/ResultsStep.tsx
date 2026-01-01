"use client";

import { useEffect, useState } from "react";
import { QuizData } from "../page";
import { PointsManager } from "../utils/pointsManager";

interface ResultsStepProps {
  score: number; // This is now a percentage (0-100)
  totalQuestions: number;
  quizData: QuizData;
  onRestart: () => void;
}

export default function ResultsStep({ score, totalQuestions, quizData, onRestart }: ResultsStepProps) {
  const percentage = score; // Score is already a percentage
  const passed = percentage >= 80; // 80% to pass (4/5 questions correct)
  const [pointsEarned, setPointsEarned] = useState(0);
  const [pointsBreakdown, setPointsBreakdown] = useState({
    base: 0,
    verification: 0,
    perfect: 0,
    first: 0
  });

  useEffect(() => {
    const manager = new PointsManager();

    // Use points awarded from API, or calculate locally if not provided
    if (passed) {
      // Use API points if available
      const apiPoints = quizData.points_awarded || 0;

      // Calculate local bonus points
      const basePoints = Math.round(percentage); // Base points from percentage score
      const perfectBonus = percentage === 100 ? 100 : 0;
      const history = manager.getQuizzes();
      const firstQuizBonus = history.length === 0 ? 50 : 0;

      // Determine verification bonus
      let verificationBonus = 0;
      if (quizData.verification?.status === "verified") {
        verificationBonus = Math.floor(basePoints * 0.5);
      } else if (quizData.verification?.status === "ai_verified") {
        verificationBonus = Math.floor(basePoints * 0.3);
      }

      const total = basePoints + verificationBonus + perfectBonus + firstQuizBonus;

      setPointsEarned(total);
      setPointsBreakdown({
        base: basePoints,
        verification: verificationBonus,
        perfect: perfectBonus,
        first: firstQuizBonus
      });

      // Save to localStorage only if passed
      manager.addPoints({
        id: Date.now().toString(),
        completedAt: new Date().toISOString(),
        score: percentage,
        totalQuestions,
        pointsEarned: total,
        sourceType: quizData.source_info?.source_type || "unknown",
        verificationStatus: quizData.verification?.status || "unknown"
      });

      // Trigger storage event for PointsDisplay component
      window.dispatchEvent(new Event('storage'));
    } else {
      // If failed, show 0 points
      setPointsEarned(0);
      setPointsBreakdown({
        base: 0,
        verification: 0,
        perfect: 0,
        first: 0
      });
    }
  }, [percentage, totalQuestions, quizData, passed]);

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
      <div className="text-center">
        <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full mb-6 ${
          passed ? "bg-green-100" : "bg-red-100"
        }`}>
          {passed ? (
            <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </div>

        <h2 className="text-4xl font-bold mb-2">
          {passed ? (
            <span className="text-green-600">Congratulations!</span>
          ) : (
            <span className="text-red-600">Keep Trying!</span>
          )}
        </h2>

        <p className="text-gray-600 text-lg mb-8">
          {passed
            ? "You passed the quiz with flying colors!"
            : "You didn't pass this time, but don't give up!"}
        </p>

        <div className="mb-8">
          <div className="inline-block bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8">
            <div className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              {Math.round(percentage)}%
            </div>
            <div className="text-gray-600 font-semibold">Your Score</div>
            <div className="text-lg text-gray-600 mt-2">Out of {totalQuestions} questions</div>
          </div>
        </div>

        {passed ? (
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 mb-8">
            <h3 className="font-bold text-lg mb-4 text-orange-800 flex items-center justify-center gap-2">
              <span>⭐</span> Points Earned <span>⭐</span>
            </h3>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-700">Base points ({Math.round(percentage)}% score)</span>
                <span className="font-semibold text-gray-900">+{pointsBreakdown.base}</span>
              </div>

              {pointsBreakdown.verification > 0 && (
                <div className="flex justify-between text-sm text-green-700">
                  <span>
                    {quizData.verification?.status === "verified" ? "Verified" : "AI-Verified"} content bonus
                  </span>
                  <span className="font-semibold">+{pointsBreakdown.verification}</span>
                </div>
              )}

              {pointsBreakdown.perfect > 0 && (
                <div className="flex justify-between text-sm text-purple-700">
                  <span>Perfect score bonus!</span>
                  <span className="font-semibold">+{pointsBreakdown.perfect}</span>
                </div>
              )}

              {pointsBreakdown.first > 0 && (
                <div className="flex justify-between text-sm text-blue-700">
                  <span>First quiz bonus!</span>
                  <span className="font-semibold">+{pointsBreakdown.first}</span>
                </div>
              )}

              <div className="border-t-2 border-orange-200 pt-2 flex justify-between text-xl font-bold">
                <span className="text-orange-800">Total Points</span>
                <span className="text-orange-600">{pointsEarned}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6 mb-8">
            <h3 className="font-bold text-lg mb-4 text-gray-700 flex items-center justify-center gap-2">
              <span>💔</span> No Points Earned <span>💔</span>
            </h3>
            <p className="text-center text-gray-600">
              You must answer at least 4 questions correctly to earn points. Try again!
            </p>
          </div>
        )}

        <div className={`mb-8 p-6 rounded-lg ${
          passed ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"
        }`}>
          <h3 className={`text-xl font-bold mb-2 ${
            passed ? "text-green-800" : "text-red-800"
          }`}>
            {passed ? "You Passed!" : "You Failed"}
          </h3>
          <p className={passed ? "text-green-700" : "text-red-700"}>
            {passed
              ? "You scored 80% or higher. Great job!"
              : "You need to score at least 80% to pass."}
          </p>
        </div>

        <div className="flex gap-4 justify-center">
          <button
            onClick={onRestart}
            className="py-3 px-8 rounded-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg"
          >
            Take Another Quiz
          </button>
        </div>
      </div>
    </div>
  );
}
