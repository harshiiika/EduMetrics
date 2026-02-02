# Visualization Module
# Creates charts and graphs for learning insights dashboard

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class InsightsVisualizer:
    """Create visualizations for student learning insights"""
    
    def __init__(self, output_dir='visualizations'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_student_progress(self, assessments_df, student_id):
        """Plot student's score progression over time"""
        student_data = assessments_df[assessments_df['student_id'] == student_id].copy()
        student_data = student_data.sort_values('assessment_date')
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(student_data['assessment_date'], student_data['score'], 
                marker='o', linewidth=2, markersize=6, alpha=0.7, label='Assessment Scores')
        
        window = min(5, len(student_data))
        if window > 1:
            rolling_avg = student_data['score'].rolling(window=window).mean()
            ax.plot(student_data['assessment_date'], rolling_avg, 
                   linewidth=3, alpha=0.8, label=f'{window}-Assessment Moving Average', 
                   color='red', linestyle='--')
        
        avg_score = student_data['score'].mean()
        ax.axhline(y=avg_score, color='green', linestyle=':', linewidth=2, 
                   label=f'Average: {avg_score:.1f}')
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title(f'Learning Progress for {student_id}', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, f'{student_id}_progress.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_subject_performance(self, assessments_df, student_id):
        """Plot performance across different subjects"""
        student_data = assessments_df[assessments_df['student_id'] == student_id]
        
        subject_scores = student_data.groupby('subject')['score'].agg(['mean', 'std', 'count'])
        subject_scores = subject_scores.sort_values('mean', ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(subject_scores))
        ax.bar(x, subject_scores['mean'], yerr=subject_scores['std'], 
               capsize=5, alpha=0.7, color='skyblue', edgecolor='navy')
        
        for i, (idx, row) in enumerate(subject_scores.iterrows()):
            ax.text(i, row['mean'] + row['std'] + 2, f"n={int(row['count'])}", 
                   ha='center', fontsize=9)
        
        ax.set_xticks(x)
        ax.set_xticklabels(subject_scores.index, rotation=45, ha='right')
        ax.set_xlabel('Subject', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Score', fontsize=12, fontweight='bold')
        ax.set_title(f'Subject Performance for {student_id}', fontsize=14, fontweight='bold')
        ax.axhline(y=70, color='orange', linestyle='--', label='Pass Threshold (70)')
        ax.axhline(y=85, color='green', linestyle='--', label='Excellence (85)')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, f'{student_id}_subjects.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_topic_heatmap(self, assessments_df, student_id):
        """Create heatmap of topic performance"""
        student_data = assessments_df[assessments_df['student_id'] == student_id]
        
        topic_pivot = student_data.pivot_table(
            values='score', 
            index='subject', 
            columns='topic', 
            aggfunc='mean'
        )
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sns.heatmap(topic_pivot, annot=True, fmt='.1f', cmap='RdYlGn', 
                   vmin=0, vmax=100, cbar_kws={'label': 'Average Score'},
                   linewidths=0.5, ax=ax)
        
        ax.set_title(f'Topic Performance Heatmap for {student_id}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Topic', fontsize=12, fontweight='bold')
        ax.set_ylabel('Subject', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, f'{student_id}_heatmap.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_study_time_analysis(self, sessions_df, student_id):
        """Analyze study time patterns"""
        student_sessions = sessions_df[sessions_df['student_id'] == student_id].copy()
        
        if len(student_sessions) == 0:
            return None
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        subject_time = student_sessions.groupby('subject')['duration_minutes'].sum().sort_values(ascending=False)
        axes[0].barh(range(len(subject_time)), subject_time.values, color='coral', alpha=0.7)
        axes[0].set_yticks(range(len(subject_time)))
        axes[0].set_yticklabels(subject_time.index)
        axes[0].set_xlabel('Total Study Time (minutes)', fontweight='bold')
        axes[0].set_title('Study Time by Subject', fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='x')
        
        completion_rate = student_sessions.groupby('subject')['completed'].mean() * 100
        completion_rate = completion_rate.sort_values(ascending=False)
        
        colors = ['green' if x >= 80 else 'orange' if x >= 60 else 'red' 
                 for x in completion_rate.values]
        
        axes[1].barh(range(len(completion_rate)), completion_rate.values, 
                    color=colors, alpha=0.7)
        axes[1].set_yticks(range(len(completion_rate)))
        axes[1].set_yticklabels(completion_rate.index)
        axes[1].set_xlabel('Completion Rate (%)', fontweight='bold')
        axes[1].set_title('Session Completion by Subject', fontweight='bold')
        axes[1].axvline(x=80, color='green', linestyle='--', alpha=0.5, label='Good (80%)')
        axes[1].axvline(x=60, color='orange', linestyle='--', alpha=0.5, label='Fair (60%)')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='x')
        
        plt.suptitle(f'Study Patterns for {student_id}', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, f'{student_id}_study_patterns.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_class_distribution(self, assessments_df):
        """Plot overall class performance distribution"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].hist(assessments_df['score'], bins=20, color='steelblue', 
                    alpha=0.7, edgecolor='black')
        axes[0].axvline(assessments_df['score'].mean(), color='red', 
                       linestyle='--', linewidth=2, label=f"Mean: {assessments_df['score'].mean():.1f}")
        axes[0].axvline(assessments_df['score'].median(), color='green', 
                       linestyle='--', linewidth=2, label=f"Median: {assessments_df['score'].median():.1f}")
        axes[0].set_xlabel('Score', fontweight='bold')
        axes[0].set_ylabel('Frequency', fontweight='bold')
        axes[0].set_title('Class Score Distribution', fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='y')
        
        subject_avg = assessments_df.groupby('subject')['score'].mean().sort_values()
        axes[1].barh(range(len(subject_avg)), subject_avg.values, color='teal', alpha=0.7)
        axes[1].set_yticks(range(len(subject_avg)))
        axes[1].set_yticklabels(subject_avg.index)
        axes[1].set_xlabel('Average Score', fontweight='bold')
        axes[1].set_title('Average Performance by Subject', fontweight='bold')
        axes[1].axvline(x=70, color='orange', linestyle='--', alpha=0.5, label='Pass (70)')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='x')
        
        plt.suptitle('Class-Level Insights', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, 'class_overview.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def plot_improvement_trends(self, assessments_df):
        """Plot which students are improving vs declining"""
        from sklearn.linear_model import LinearRegression
        
        student_trends = []
        
        for student_id in assessments_df['student_id'].unique():
            student_data = assessments_df[assessments_df['student_id'] == student_id].copy()
            student_data = student_data.sort_values('assessment_date')
            
            if len(student_data) < 5:
                continue
            
            X = np.arange(len(student_data)).reshape(-1, 1)
            y = student_data['score'].values
            
            model = LinearRegression()
            model.fit(X, y)
            slope = model.coef_[0]
            
            student_trends.append({
                'student_id': student_id,
                'trend_slope': slope,
                'avg_score': student_data['score'].mean()
            })
        
        trends_df = pd.DataFrame(student_trends)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        scatter = ax.scatter(trends_df['avg_score'], trends_df['trend_slope'], 
                           s=100, alpha=0.6, c=trends_df['trend_slope'], 
                           cmap='RdYlGn', edgecolors='black', linewidth=0.5)
        
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)
        ax.axvline(x=70, color='orange', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('Average Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Improvement Trend (Slope)', fontsize=12, fontweight='bold')
        ax.set_title('Student Performance Trends', fontsize=14, fontweight='bold')
        
        plt.colorbar(scatter, label='Trend Direction', ax=ax)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, 'class_trends.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_student_dashboard(self, assessments_df, sessions_df, student_id):
        """Create complete dashboard for a student"""
        print(f"Creating dashboard for {student_id}...")
        
        visualizations = {}
        
        visualizations['progress'] = self.plot_student_progress(assessments_df, student_id)
        visualizations['subjects'] = self.plot_subject_performance(assessments_df, student_id)
        visualizations['heatmap'] = self.plot_topic_heatmap(assessments_df, student_id)
        
        study_viz = self.plot_study_time_analysis(sessions_df, student_id)
        if study_viz:
            visualizations['study_patterns'] = study_viz
        
        print(f"Dashboard created successfully for {student_id}")
        return visualizations