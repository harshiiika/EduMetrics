"""
Learning Insights Analyzer
Core logic for generating meaningful insights from student data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')


class LearningInsightsAnalyzer:
    """Analyze student data and generate actionable learning insights"""
    
    def __init__(self, students_df, assessments_df, sessions_df):
        self.students = students_df
        self.assessments = assessments_df
        self.sessions = sessions_df
        
        if 'assessment_date' in self.assessments.columns:
            self.assessments['assessment_date'] = pd.to_datetime(self.assessments['assessment_date'])
        if 'session_date' in self.sessions.columns:
            self.sessions['session_date'] = pd.to_datetime(self.sessions['session_date'])
    
    def get_student_performance_summary(self, student_id):
        """Get comprehensive performance summary for a student"""
        student_assessments = self.assessments[self.assessments['student_id'] == student_id]
        student_sessions = self.sessions[self.sessions['student_id'] == student_id]
        
        if len(student_assessments) == 0:
            return None
        
        summary = {
            'student_id': student_id,
            'total_assessments': len(student_assessments),
            'average_score': student_assessments['score'].mean(),
            'median_score': student_assessments['score'].median(),
            'score_std': student_assessments['score'].std(),
            'best_subject': student_assessments.groupby('subject')['score'].mean().idxmax(),
            'weakest_subject': student_assessments.groupby('subject')['score'].mean().idxmin(),
            'total_study_time': student_sessions['duration_minutes'].sum(),
            'completion_rate': student_sessions['completed'].mean() * 100,
            'improvement_trend': self._calculate_improvement_trend(student_assessments)
        }
        
        return summary
    
    def _calculate_improvement_trend(self, assessments_df):
        """Calculate if student is improving over time"""
        if len(assessments_df) < 5:
            return 'Insufficient Data'
        
        df = assessments_df.sort_values('assessment_date').reset_index(drop=True)
        
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['score'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = model.coef_[0]
        
        if slope > 0.5:
            return 'Strong Improvement'
        elif slope > 0.1:
            return 'Moderate Improvement'
        elif slope > -0.1:
            return 'Stable'
        elif slope > -0.5:
            return 'Slight Decline'
        else:
            return 'Needs Attention'
    
    def identify_weak_topics(self, student_id, threshold=70):
        """Identify topics where student is struggling"""
        student_data = self.assessments[self.assessments['student_id'] == student_id]
        
        topic_performance = student_data.groupby(['subject', 'topic']).agg({
            'score': ['mean', 'count']
        }).reset_index()
        
        topic_performance.columns = ['subject', 'topic', 'avg_score', 'attempts']
        
        weak_topics = topic_performance[topic_performance['avg_score'] < threshold]
        weak_topics = weak_topics.sort_values('avg_score')
        
        return weak_topics[['subject', 'topic', 'avg_score', 'attempts']].to_dict('records')
    
    def identify_strong_topics(self, student_id, threshold=85):
        """Identify topics where student excels"""
        student_data = self.assessments[self.assessments['student_id'] == student_id]
        
        topic_performance = student_data.groupby(['subject', 'topic']).agg({
            'score': ['mean', 'count']
        }).reset_index()
        
        topic_performance.columns = ['subject', 'topic', 'avg_score', 'attempts']
        
        strong_topics = topic_performance[topic_performance['avg_score'] >= threshold]
        strong_topics = strong_topics.sort_values('avg_score', ascending=False)
        
        return strong_topics[['subject', 'topic', 'avg_score', 'attempts']].to_dict('records')
    
    def predict_performance(self, student_id, subject):
        """Predict likely performance on next assessment"""
        student_data = self.assessments[
            (self.assessments['student_id'] == student_id) & 
            (self.assessments['subject'] == subject)
        ].copy()
        
        if len(student_data) < 3:
            return {'prediction': None, 'confidence': 'Low', 'message': 'Insufficient data'}
        
        student_data = student_data.sort_values('assessment_date').reset_index(drop=True)
        
        recent_scores = student_data.tail(5)['score'].values
        
        weights = np.array([0.1, 0.15, 0.2, 0.25, 0.3])[:len(recent_scores)]
        weights = weights / weights.sum()
        
        predicted_score = np.average(recent_scores, weights=weights)
        
        score_std = recent_scores.std()
        if score_std < 5:
            confidence = 'High'
        elif score_std < 10:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        return {
            'prediction': round(predicted_score, 2),
            'confidence': confidence,
            'recent_trend': self._calculate_improvement_trend(student_data)
        }
    
    def get_study_recommendations(self, student_id):
        """Generate personalized study recommendations"""
        weak_topics = self.identify_weak_topics(student_id, threshold=70)
        student_sessions = self.sessions[self.sessions['student_id'] == student_id]
        
        recommendations = []
        
        if weak_topics:
            top_weak = weak_topics[:3]
            recommendations.append({
                'priority': 'High',
                'type': 'Skill Gap',
                'message': f"Focus on improving: {', '.join([t['topic'] for t in top_weak])}",
                'details': top_weak
            })
        
        if len(student_sessions) > 0:
            completion_rate = student_sessions['completed'].mean()
            if completion_rate < 0.7:
                recommendations.append({
                    'priority': 'Medium',
                    'type': 'Study Habits',
                    'message': f"Improve study session completion rate (currently {completion_rate*100:.1f}%)",
                    'suggestion': 'Break study sessions into smaller, manageable chunks'
                })
        
        student_data = self.assessments[self.assessments['student_id'] == student_id]
        if len(student_data) > 0:
            avg_time = student_data['time_spent_minutes'].mean()
            if avg_time < 20:
                recommendations.append({
                    'priority': 'Low',
                    'type': 'Time Investment',
                    'message': 'Consider spending more time on assessments for better understanding',
                    'current_avg': f"{avg_time:.1f} minutes"
                })
        
        return recommendations
    
    def get_class_insights(self):
        """Generate class-level insights"""
        insights = {
            'total_students': len(self.students),
            'total_assessments': len(self.assessments),
            'class_average': self.assessments['score'].mean(),
            'top_performers': self._get_top_students(n=5),
            'struggling_students': self._get_struggling_students(n=5),
            'subject_difficulty': self._analyze_subject_difficulty(),
            'engagement_metrics': self._analyze_engagement()
        }
        
        return insights
    
    def _get_top_students(self, n=5):
        """Get top performing students"""
        student_avg = self.assessments.groupby('student_id')['score'].mean()
        top_students = student_avg.nlargest(n)
        
        return [{'student_id': sid, 'average_score': score} 
                for sid, score in top_students.items()]
    
    def _get_struggling_students(self, n=5):
        """Get students who need support"""
        student_avg = self.assessments.groupby('student_id')['score'].mean()
        struggling = student_avg.nsmallest(n)
        
        return [{'student_id': sid, 'average_score': score} 
                for sid, score in struggling.items()]
    
    def _analyze_subject_difficulty(self):
        """Analyze which subjects are most challenging"""
        subject_stats = self.assessments.groupby('subject')['score'].agg(['mean', 'std', 'count'])
        subject_stats = subject_stats.sort_values('mean')
        
        return subject_stats.to_dict('index')
    
    def _analyze_engagement(self):
        """Analyze overall student engagement"""
        total_sessions = len(self.sessions)
        completed_sessions = self.sessions['completed'].sum()
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        avg_session_duration = self.sessions['duration_minutes'].mean()
        
        return {
            'total_sessions': total_sessions,
            'completion_rate': round(completion_rate, 2),
            'avg_session_duration': round(avg_session_duration, 2)
        }
    
    def generate_insight_report(self, student_id):
        """Generate comprehensive insight report for a student"""
        summary = self.get_student_performance_summary(student_id)
        if not summary:
            return {'error': 'No data available for this student'}
        
        weak_topics = self.identify_weak_topics(student_id)
        strong_topics = self.identify_strong_topics(student_id)
        recommendations = self.get_study_recommendations(student_id)
        
        subjects = self.assessments[self.assessments['student_id'] == student_id]['subject'].unique()
        predictions = {}
        for subject in subjects:
            predictions[subject] = self.predict_performance(student_id, subject)
        
        report = {
            'student_id': student_id,
            'generated_at': datetime.now().isoformat(),
            'performance_summary': summary,
            'weak_topics': weak_topics,
            'strong_topics': strong_topics,
            'subject_predictions': predictions,
            'recommendations': recommendations
        }
        
        return report