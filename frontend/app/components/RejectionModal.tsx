interface RejectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  reason: string;
  confidence?: number;
}

export default function RejectionModal({ isOpen, onClose, reason, confidence }: RejectionModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-red-800 mb-2">Content Rejected</h2>
          <p className="text-gray-600">This content does not meet our educational standards</p>
        </div>

        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium mb-2">Reason:</p>
          <p className="text-red-700">{reason}</p>

          {confidence !== undefined && (
            <p className="text-sm text-red-600 mt-3">
              AI Confidence: {confidence.toFixed(1)}% (minimum required: 70%)
            </p>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800 font-semibold mb-2">
            What content is accepted?
          </p>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Educational videos and courses</li>
            <li>• Academic lectures and tutorials</li>
            <li>• Professional development content</li>
            <li>• Skill-building resources</li>
            <li>• Research papers and articles</li>
          </ul>
        </div>

        <button
          onClick={onClose}
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
        >
          Try Different Content
        </button>
      </div>
    </div>
  );
}
