import { VerificationMetadata } from "../page";

interface VerificationBadgeProps {
  verification: VerificationMetadata;
}

export default function VerificationBadge({ verification }: VerificationBadgeProps) {
  if (verification.status === "verified") {
    return (
      <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-lg px-4 py-3 shadow-sm">
        <div className="flex-shrink-0">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="font-semibold text-green-800">Verified Educational Content</p>
          <p className="text-sm text-green-600">
            From {verification.platform} - a trusted learning platform
          </p>
        </div>
      </div>
    );
  }

  if (verification.status === "ai_verified") {
    return (
      <div className="flex items-center gap-3 bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 shadow-sm">
        <div className="flex-shrink-0">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="font-semibold text-blue-800">AI-Verified Educational Content</p>
          <p className="text-sm text-blue-600">
            Confidence: {verification.confidenceScore?.toFixed(1)}% | Quality content for learning
          </p>
        </div>
      </div>
    );
  }

  if (verification.status === "pending") {
    return (
      <div className="flex items-center gap-3 bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-3 shadow-sm">
        <div className="flex-shrink-0">
          <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="font-semibold text-yellow-800">Unverified Content</p>
          <p className="text-sm text-yellow-600">
            Educational verification unavailable - points will not include verification bonus
          </p>
        </div>
      </div>
    );
  }

  return null;
}
