export interface QuizRecord {
  id: string;
  completedAt: string;
  score: number;
  totalQuestions: number;
  pointsEarned: number;
  sourceType: string;
  verificationStatus: string;
}

export interface PointsHistory {
  totalPoints: number;
  quizzes: QuizRecord[];
  firstQuizCompleted: boolean;
}

const STORAGE_KEY = 'quiz_points_history';

export class PointsManager {
  private getHistory(): PointsHistory {
    if (typeof window === 'undefined') {
      return { totalPoints: 0, quizzes: [], firstQuizCompleted: false };
    }

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        return { totalPoints: 0, quizzes: [], firstQuizCompleted: false };
      }
      return JSON.parse(stored);
    } catch (error) {
      console.error('Failed to load points history:', error);
      return { totalPoints: 0, quizzes: [], firstQuizCompleted: false };
    }
  }

  private saveHistory(history: PointsHistory): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Failed to save points history:', error);
    }
  }

  addPoints(quiz: QuizRecord): void {
    const history = this.getHistory();

    history.quizzes.push(quiz);
    history.totalPoints += quiz.pointsEarned;

    // Mark first quiz as completed if this is the first
    if (!history.firstQuizCompleted && history.quizzes.length === 1) {
      history.firstQuizCompleted = true;
    }

    this.saveHistory(history);
  }

  getTotal(): number {
    return this.getHistory().totalPoints;
  }

  getQuizzes(): QuizRecord[] {
    return this.getHistory().quizzes;
  }

  clearHistory(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(STORAGE_KEY);
  }

  exportHistory(): string {
    return JSON.stringify(this.getHistory(), null, 2);
  }

  importHistory(jsonString: string): boolean {
    try {
      const history = JSON.parse(jsonString) as PointsHistory;
      this.saveHistory(history);
      return true;
    } catch (error) {
      console.error('Failed to import history:', error);
      return false;
    }
  }

  calculatePoints(
    score: number,
    totalQuestions: number,
    verificationStatus: string
  ): number {
    // Base points: 10 per correct answer
    const basePoints = score * 10;

    // Verification bonus
    let verificationBonus = 0;
    if (verificationStatus === 'verified') {
      verificationBonus = Math.floor(basePoints * 0.5); // 50% bonus
    } else if (verificationStatus === 'ai_verified') {
      verificationBonus = Math.floor(basePoints * 0.3); // 30% bonus
    }

    // Perfect score bonus
    const perfectBonus = score === totalQuestions ? 100 : 0;

    // First quiz bonus
    const history = this.getHistory();
    const firstQuizBonus = !history.firstQuizCompleted ? 50 : 0;

    return basePoints + verificationBonus + perfectBonus + firstQuizBonus;
  }
}
