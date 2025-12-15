"use client";

interface ResultsStepProps {
  score: number;
  totalQuestions: number;
  onRestart: () => void;
}

export default function ResultsStep({ score, totalQuestions, onRestart }: ResultsStepProps) {
  const passed = score >= 4;
  const percentage = (score / totalQuestions) * 100;

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
              {score}/{totalQuestions}
            </div>
            <div className="text-gray-600 font-semibold">Questions Correct</div>
            <div className="text-2xl font-bold text-gray-700 mt-2">{percentage}%</div>
          </div>
        </div>

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
              ? "You answered 4 or more questions correctly. Great job!"
              : "You need to answer at least 4 questions correctly to pass."}
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
