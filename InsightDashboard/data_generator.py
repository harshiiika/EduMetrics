# Student Learning Data Generator
# Simulates realistic student performance data for the insights dashboard


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

np.random.seed(42)

class StudentDataGenerator:
    # Generate realistic student learning data
    
    def __init__(self, num_students=100):
        self.num_students = num_students
        self.subjects = ['Mathematics', 'Science', 'English', 'History', 'Computer Science']
        self.topics_per_subject = {
            'Mathematics': ['Algebra', 'Geometry', 'Calculus', 'Statistics', 'Trigonometry'],
            'Science': ['Physics', 'Chemistry', 'Biology', 'Environmental Science', 'Lab Skills'],
            'English': ['Grammar', 'Literature', 'Writing', 'Reading Comprehension', 'Vocabulary'],
            'History': ['Ancient History', 'Modern History', 'Geography', 'Civics', 'World Wars'],
            'Computer Science': ['Programming', 'Data Structures', 'Algorithms', 'Databases', 'Web Development']
        }
        
    def generate_student_profiles(self):
        # Generate basic student profiles
        students = []
        
        for i in range(self.num_students):
            base_ability = np.random.normal(70, 15)
            learning_rate = np.random.uniform(0.5, 2.0)
            engagement = np.random.uniform(0.3, 1.0)
            
            student = {
                'student_id': f'STU{i+1:03d}',
                'name': f'Student {i+1}',
                'grade_level': np.random.choice([9, 10, 11, 12]),
                'base_ability': base_ability,
                'learning_rate': learning_rate,
                'engagement_level': engagement,
                'study_hours_per_week': np.random.randint(5, 30)
            }
            students.append(student)
            
        return pd.DataFrame(students)
    
    def generate_assessment_data(self, students_df):
        """Generate assessment/quiz results over time"""
        assessments = []
        start_date = datetime.now() - timedelta(days=180)
        
        for _, student in students_df.iterrows():
            num_assessments = np.random.randint(20, 31)
            
            for assessment_num in range(num_assessments):
                subject = np.random.choice(self.subjects)
                topic = np.random.choice(self.topics_per_subject[subject])
                
                days_offset = np.random.randint(0, 180)
                assessment_date = start_date + timedelta(days=days_offset)
                
                progress_factor = (assessment_num / num_assessments) * student['learning_rate']
                engagement_factor = student['engagement_level']
                
                base_score = student['base_ability']
                improvement = progress_factor * 10
                random_variation = np.random.normal(0, 5)
                
                score = base_score + improvement + random_variation
                score = max(0, min(100, score))
                
                time_spent = np.random.randint(15, 90)
                attempts = np.random.choice([1, 1, 1, 2, 2, 3], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])
                
                assessment = {
                    'student_id': student['student_id'],
                    'subject': subject,
                    'topic': topic,
                    'assessment_date': assessment_date,
                    'score': round(score, 2),
                    'max_score': 100,
                    'time_spent_minutes': time_spent,
                    'attempts': attempts,
                    'difficulty_level': np.random.choice(['Easy', 'Medium', 'Hard'])
                }
                assessments.append(assessment)
        
        df = pd.DataFrame(assessments)
        df = df.sort_values(['student_id', 'assessment_date']).reset_index(drop=True)
        return df
    
    def generate_study_sessions(self, students_df):
        """Generate study session logs"""
        sessions = []
        start_date = datetime.now() - timedelta(days=180)
        
        for _, student in students_df.iterrows():
            sessions_per_week = student['study_hours_per_week'] / 2
            total_sessions = int(sessions_per_week * 26)
            
            for session_num in range(total_sessions):
                days_offset = np.random.randint(0, 180)
                session_date = start_date + timedelta(days=days_offset)
                
                subject = np.random.choice(self.subjects)
                
                base_duration = 30
                duration = int(base_duration * student['engagement_level'] * np.random.uniform(0.8, 2.0))
                
                session = {
                    'student_id': student['student_id'],
                    'session_date': session_date,
                    'subject': subject,
                    'duration_minutes': duration,
                    'completed': np.random.choice([True, False], p=[0.85, 0.15])
                }
                sessions.append(session)
        
        df = pd.DataFrame(sessions)
        df = df.sort_values(['student_id', 'session_date']).reset_index(drop=True)
        return df
    
    def generate_all_data(self):
        """Generate complete dataset"""
        print("Generating student profiles...")
        students_df = self.generate_student_profiles()
        
        print("Generating assessment data...")
        assessments_df = self.generate_assessment_data(students_df)
        
        print("Generating study sessions...")
        sessions_df = self.generate_study_sessions(students_df)
        
        return students_df, assessments_df, sessions_df
    
    def save_data(self, students_df, assessments_df, sessions_df, format='csv'):
        """Save generated data to files"""
        import os
        os.makedirs('data', exist_ok=True)
        
        if format == 'csv':
            students_df.to_csv('data/students.csv', index=False)
            assessments_df.to_csv('data/assessments.csv', index=False)
            sessions_df.to_csv('data/study_sessions.csv', index=False)
            print("Data saved as CSV files in 'data/' directory")
        elif format == 'json':
            students_df.to_json('data/students.json', orient='records', indent=2)
            assessments_df.to_json('data/assessments.json', orient='records', indent=2, date_format='iso')
            sessions_df.to_json('data/study_sessions.json', orient='records', indent=2, date_format='iso')
            print("Data saved as JSON files in 'data/' directory")