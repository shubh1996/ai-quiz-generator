"use client";

import { useState, useEffect } from "react";
import { PointsManager } from "../utils/pointsManager";

export default function PointsDisplay() {
  const [points, setPoints] = useState(0);

  useEffect(() => {
    const manager = new PointsManager();
    setPoints(manager.getTotal());

    // Listen for storage changes (if user completes quiz in another tab)
    const handleStorageChange = () => {
      setPoints(manager.getTotal());
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <div className="fixed top-4 right-4 bg-white rounded-lg shadow-lg px-6 py-3 border border-purple-100 z-10">
      <div className="flex items-center gap-3">
        <span className="text-3xl">⭐</span>
        <div>
          <p className="text-xs text-gray-600 font-medium">Total Points</p>
          <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            {points.toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}
