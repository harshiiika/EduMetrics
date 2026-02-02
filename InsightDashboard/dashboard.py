# Student Learning Insights Dashboard
# Main application that generates comprehensive learning insights

import pandas as pd
import json
from datetime import datetime
import os

from data_generator import StudentDataGenerator
from insights_analyzer import LearningInsightsAnalyzer
from visualizer import InsightsVisualizer


class LearningInsightsDashboard:
#    Main dashboard application
    
    def __init__(self, data_path='data'):
        self.data_path = data_path
        self.students = None
        self.assessments = None
        self.sessions = None
        self.analyzer = None
        self.visualizer = InsightsVisualizer()
    
    def generate_sample_data(self, num_students=100):
        """Generate sample dataset"""
        print("=" * 60)
        print("GENERATING SAMPLE STUDENT DATA")
        print("=" * 60)
        
        generator = StudentDataGenerator(num_students=num_students)
        self.students, self.assessments, self.sessions = generator.generate_all_data()
        generator.save_data(self.students, self.assessments, self.sessions, format='csv')
        generator.save_data(self.students, self.assessments, self.sessions, format='json')
        
        print(f"\n✓ Generated data for {num_students} students")
        print(f"✓ Total assessments: {len(self.assessments)}")
        print(f"✓ Total study sessions: {len(self.sessions)}")
    
    def load_data(self):
        """Load existing data"""
        print("\nLoading data from files...")
        
        self.students = pd.read_csv(f'{self.data_path}/students.csv')
        self.assessments = pd.read_csv(f'{self.data_path}/assessments.csv')
        self.sessions = pd.read_csv(f'{self.data_path}/study_sessions.csv')
        
        self.assessments['assessment_date'] = pd.to_datetime(self.assessments['assessment_date'])
        self.sessions['session_date'] = pd.to_datetime(self.sessions['session_date'])
        
        print(f"✓ Loaded {len(self.students)} students")
        print(f"✓ Loaded {len(self.assessments)} assessments")
        print(f"✓ Loaded {len(self.sessions)} study sessions")
        
        self.analyzer = LearningInsightsAnalyzer(
            self.students, self.assessments, self.sessions
        )
    
    def generate_student_report(self, student_id, output_format='json'):
        """Generate comprehensive report for a student"""
        print(f"\n{'=' * 60}")
        print(f"GENERATING INSIGHTS FOR {student_id}")
        print(f"{'=' * 60}")
        
        report = self.analyzer.generate_insight_report(student_id)
        
        print("\nCreating visualizations...")
        visualizations = self.visualizer.create_student_dashboard(
            self.assessments, self.sessions, student_id
        )
        
        report['visualizations'] = visualizations
        
        os.makedirs('reports', exist_ok=True)
        
        if output_format == 'json':
            report_path = f'reports/{student_id}_report.json'
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n✓ Report saved: {report_path}")
        
        print(f"\n{'=' * 60}")
        print("INSIGHTS SUMMARY")
        print(f"{'=' * 60}")
        
        summary = report['performance_summary']
        print(f"\nStudent ID: {student_id}")
        print(f"Average Score: {summary['average_score']:.2f}")
        print(f"Total Assessments: {summary['total_assessments']}")
        print(f"Best Subject: {summary['best_subject']}")
        print(f"Weakest Subject: {summary['weakest_subject']}")
        print(f"Improvement Trend: {summary['improvement_trend']}")
        print(f"Study Completion Rate: {summary['completion_rate']:.1f}%")
        
        if report['weak_topics']:
            print(f"\nTop 3 Topics Needing Attention:")
            for i, topic in enumerate(report['weak_topics'][:3], 1):
                print(f"  {i}. {topic['subject']} - {topic['topic']} (Avg: {topic['avg_score']:.1f})")
        
        if report['recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. [{rec['priority']}] {rec['message']}")
        
        return report
    
    def generate_class_insights(self):
        """Generate class-level insights"""
        print(f"\n{'=' * 60}")
        print("CLASS-LEVEL INSIGHTS")
        print(f"{'=' * 60}")
        
        insights = self.analyzer.get_class_insights()
        
        print(f"\nTotal Students: {insights['total_students']}")
        print(f"Total Assessments: {insights['total_assessments']}")
        print(f"Class Average: {insights['class_average']:.2f}")
        
        print(f"\nTop 5 Performers:")
        for i, student in enumerate(insights['top_performers'], 1):
            print(f"  {i}. {student['student_id']}: {student['average_score']:.2f}")
        
        print(f"\nStudents Needing Support:")
        for i, student in enumerate(insights['struggling_students'], 1):
            print(f"  {i}. {student['student_id']}: {student['average_score']:.2f}")
        
        print(f"\nSubject Difficulty (Easiest to Hardest):")
        for subject, stats in sorted(insights['subject_difficulty'].items(), 
                                    key=lambda x: x[1]['mean'], reverse=True):
            print(f"  {subject}: {stats['mean']:.2f} (±{stats['std']:.2f})")
        
        print("\nCreating class-level visualizations...")
        self.visualizer.plot_class_distribution(self.assessments)
        self.visualizer.plot_improvement_trends(self.assessments)
        
        os.makedirs('reports', exist_ok=True)
        with open('reports/class_insights.json', 'w') as f:
            json.dump(insights, f, indent=2, default=str)
        
        print(f"\n✓ Class insights saved: reports/class_insights.json")
        
        return insights
    
    def run_demo(self):
        """Run complete demo"""
        print("\n" + "=" * 60)
        print("STUDENT LEARNING INSIGHTS DASHBOARD - DEMO")
        print("=" * 60)
        
        if not os.path.exists(f'{self.data_path}/students.csv'):
            print("\nNo existing data found. Generating sample data...")
            self.generate_sample_data(num_students=100)
        
        self.load_data()
        
        self.generate_class_insights()
        
        sample_students = self.students.head(3)['student_id'].tolist()
        
        print(f"\n{'=' * 60}")
        print(f"GENERATING SAMPLE STUDENT REPORTS")
        print(f"{'=' * 60}")
        
        for student_id in sample_students:
            self.generate_student_report(student_id)
        
        print(f"\n{'=' * 60}")
        print("DEMO COMPLETED SUCCESSFULLY!")
        print(f"{'=' * 60}")
        print("\nGenerated Files:")
        print("  - data/ : Student data (CSV and JSON)")
        print("  - reports/ : Insight reports (JSON)")
        print("  - visualizations/ : Charts and graphs (PNG)")


def main():
    """Main entry point"""
    dashboard = LearningInsightsDashboard()
    dashboard.run_demo()


if __name__ == "__main__":
    main()