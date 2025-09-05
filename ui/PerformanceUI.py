import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.auth import login_required, init_session_state
from ui.icons import get_svg_icon, icon_text, info_message
from utils.config import get_database, COLLECTIONS

class PerformanceAnalytics:
    """Enhanced Performance Analytics with MongoDB integration"""
    
    def __init__(self, user_id):
        # Handle both string and integer user IDs
        self.user_id = str(user_id) if user_id else None
        self.db = get_database()
        self.results_collection = self.db[COLLECTIONS["quiz_results"]] if self.db is not None else None
    
    def get_user_quiz_results(self) -> List[Dict]:
        """Fetch all quiz results for the current user"""
        if self.results_collection is None:
            return []
        
        try:
            results = list(self.results_collection.find(
                {"user_id": self.user_id}
            ).sort("_id", -1))
            return results
        except Exception as e:
            st.error(f"Error fetching quiz results: {str(e)}")
            return []
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        results = self.get_user_quiz_results()
        
        if not results:
            return {
                "total_quizzes": 0,
                "average_score": 0,
                "total_questions": 0,
                "accuracy_percentage": 0,
                "study_streak": 0,
                "recent_activity": [],
                "topic_performance": {},
                "improvement_trend": [],
                "strengths": [],
                "weaknesses": []
            }
        
        # Basic metrics
        total_quizzes = len(results)
        total_score = sum(r.get("result", {}).get("score", 0) for r in results)
        total_questions = sum(r.get("result", {}).get("total", 0) for r in results)
        average_score = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        # Topic-wise performance
        topic_performance = {}
        for result in results:
            topic = result.get("topic", "Unknown")
            if topic not in topic_performance:
                topic_performance[topic] = {"scores": [], "total_questions": 0, "correct_answers": 0}
            
            score = result.get("result", {}).get("score", 0)
            total = result.get("result", {}).get("total", 1)
            topic_performance[topic]["scores"].append((score / total) * 100)
            topic_performance[topic]["total_questions"] += total
            topic_performance[topic]["correct_answers"] += score
        
        # Calculate average for each topic
        for topic in topic_performance:
            scores = topic_performance[topic]["scores"]
            topic_performance[topic]["average"] = sum(scores) / len(scores) if scores else 0
        
        # Recent activity (last 10 quizzes)
        recent_activity = []
        for result in results[:10]:
            recent_activity.append({
                "topic": result.get("topic", "Unknown"),
                "score": result.get("result", {}).get("score", 0),
                "total": result.get("result", {}).get("total", 1),
                "accuracy": result.get("result", {}).get("accuracy", 0),
                "date": result.get("_id").generation_time if result.get("_id") else datetime.now()
            })
        
        # Improvement trend (last 5 quizzes)
        improvement_trend = []
        for result in results[:5]:
            improvement_trend.append({
                "accuracy": result.get("result", {}).get("accuracy", 0),
                "date": result.get("_id").generation_time if result.get("_id") else datetime.now()
            })
        
        # Strengths and weaknesses
        strengths = [topic for topic, data in topic_performance.items() if data["average"] >= 80]
        weaknesses = [topic for topic, data in topic_performance.items() if data["average"] < 60]
        
        return {
            "total_quizzes": total_quizzes,
            "average_score": average_score,
            "total_questions": total_questions,
            "accuracy_percentage": average_score,
            "study_streak": self._calculate_study_streak(results),
            "recent_activity": recent_activity,
            "topic_performance": topic_performance,
            "improvement_trend": improvement_trend,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    def _calculate_study_streak(self, results: List[Dict]) -> int:
        """Calculate current study streak in days"""
        if not results:
            return 0
        
        # Simple streak calculation based on quiz dates
        dates = []
        for result in results:
            if result.get("_id"):
                dates.append(result["_id"].generation_time.date())
        
        if not dates:
            return 0
        
        dates = sorted(set(dates), reverse=True)
        streak = 0
        current_date = datetime.now().date()
        
        for date in dates:
            if (current_date - date).days == streak:
                streak += 1
            else:
                break
        
        return streak

def render_performance_metrics(metrics: Dict[str, Any]):
    """Render enhanced performance metrics with modern cards"""
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-icon {
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{get_svg_icon('quiz', 32, '#667eea')}</div>
            <div class="metric-value">{metrics['total_quizzes']}</div>
            <div class="metric-label">Quizzes Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        accuracy_color = '#22c55e' if metrics['accuracy_percentage'] >= 70 else '#f59e0b' if metrics['accuracy_percentage'] >= 50 else '#ef4444'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{get_svg_icon('target', 32, accuracy_color)}</div>
            <div class="metric-value">{metrics['accuracy_percentage']:.1f}%</div>
            <div class="metric-label">Average Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{get_svg_icon('timer', 32, '#8b5cf6')}</div>
            <div class="metric-value">{metrics['study_streak']}</div>
            <div class="metric-label">Study Streak (Days)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{get_svg_icon('chart', 32, '#06b6d4')}</div>
            <div class="metric-value">{metrics['total_questions']}</div>
            <div class="metric-label">Total Questions</div>
        </div>
        """, unsafe_allow_html=True)

def render_performance_charts(metrics: Dict[str, Any]):
    """Render interactive performance charts"""
    if not metrics['recent_activity']:
        st.info("Complete some quizzes to see your performance charts!")
        return
    
    # Recent Performance Trend
    st.markdown(icon_text("analytics", "Performance Trends", 20), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Accuracy trend chart
        if metrics['improvement_trend']:
            trend_data = pd.DataFrame(metrics['improvement_trend'])
            fig = px.line(
                trend_data, 
                x='date', 
                y='accuracy',
                title='📈 Accuracy Improvement Trend',
                line_shape='spline',
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Topic performance pie chart
        if metrics['topic_performance']:
            topic_data = []
            for topic, data in metrics['topic_performance'].items():
                topic_data.append({
                    'topic': topic,
                    'average': data['average'],
                    'questions': data['total_questions']
                })
            
            if topic_data:
                df = pd.DataFrame(topic_data)
                fig = px.pie(
                    df, 
                    values='questions', 
                    names='topic',
                    title='🎯 Questions by Topic',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

def render_topic_analysis(metrics: Dict[str, Any]):
    """Render detailed topic-wise performance analysis"""
    st.markdown(icon_text("brain", "Topic Performance Analysis", 20), unsafe_allow_html=True)
    
    if not metrics['topic_performance']:
        st.info("Complete quizzes in different topics to see your topic analysis!")
        return
    
    # Create topic performance dataframe
    topic_data = []
    for topic, data in metrics['topic_performance'].items():
        topic_data.append({
            'Topic': topic,
            'Average Score': f"{data['average']:.1f}%",
            'Questions Answered': data['total_questions'],
            'Correct Answers': data['correct_answers'],
            'Performance': '🟢 Strong' if data['average'] >= 80 else '🟡 Good' if data['average'] >= 60 else '🔴 Needs Work'
        })
    
    df = pd.DataFrame(topic_data)
    st.dataframe(df, use_container_width=True)
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💪 Your Strengths")
        if metrics['strengths']:
            for strength in metrics['strengths']:
                avg_score = metrics['topic_performance'][strength]['average']
                st.success(f"**{strength}** - {avg_score:.1f}% average")
        else:
            st.info("Keep practicing to identify your strengths!")
    
    with col2:
        st.markdown("### 📚 Areas for Improvement")
        if metrics['weaknesses']:
            for weakness in metrics['weaknesses']:
                avg_score = metrics['topic_performance'][weakness]['average']
                st.warning(f"**{weakness}** - {avg_score:.1f}% average")
        else:
            st.success("Great job! No weak areas identified.")

def render_recent_activity(metrics: Dict[str, Any]):
    """Render recent quiz activity timeline"""
    st.markdown(icon_text("history", "Recent Activity", 20), unsafe_allow_html=True)
    
    if not metrics['recent_activity']:
        st.info("Take some quizzes to see your recent activity!")
        return
    
    for activity in metrics['recent_activity']:
        accuracy = (activity['score'] / activity['total']) * 100
        
        # Color coding based on performance
        if accuracy >= 80:
            color = "success"
            icon = "check_circle"
        elif accuracy >= 60:
            color = "warning"
            icon = "target"
        else:
            color = "error"
            icon = "refresh"
        
        with st.container():
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 1rem;
                margin: 0.5rem 0;
                border-left: 4px solid {'#22c55e' if color == 'success' else '#f59e0b' if color == 'warning' else '#ef4444'};
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {get_svg_icon(icon, 20, '#22c55e' if color == 'success' else '#f59e0b' if color == 'warning' else '#ef4444')}
                    <strong>{activity['topic']}</strong>
                    <span style="margin-left: auto;">{accuracy:.1f}%</span>
                </div>
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-top: 0.5rem;">
                    Score: {activity['score']}/{activity['total']} • {activity['date'].strftime('%B %d, %Y')}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_ai_insights(metrics: Dict[str, Any]):
    """Render AI-powered insights and recommendations"""
    st.markdown(icon_text("light_bulb", "AI-Powered Insights", 20), unsafe_allow_html=True)
    
    if metrics['total_quizzes'] == 0:
        st.info("🤖 Complete some quizzes to get personalized AI insights!")
        return
    
    # Generate insights based on performance
    insights = []
    
    # Performance insights
    if metrics['accuracy_percentage'] >= 80:
        insights.append({
            'type': 'success',
            'title': 'Excellent Performance! 🎉',
            'message': f"You're scoring an average of {metrics['accuracy_percentage']:.1f}%. Keep up the fantastic work!"
        })
    elif metrics['accuracy_percentage'] >= 60:
        insights.append({
            'type': 'info',
            'title': 'Good Progress! 📈',
            'message': f"You're averaging {metrics['accuracy_percentage']:.1f}%. Focus on your weak areas to reach the next level."
        })
    else:
        insights.append({
            'type': 'warning',
            'title': 'Room for Improvement 💪',
            'message': f"Your average is {metrics['accuracy_percentage']:.1f}%. Consider reviewing fundamentals and practicing more."
        })
    
    # Study streak insights
    if metrics['study_streak'] >= 7:
        insights.append({
            'type': 'success',
            'title': 'Amazing Consistency! 🔥',
            'message': f"You've maintained a {metrics['study_streak']}-day study streak. Consistency is key to success!"
        })
    elif metrics['study_streak'] >= 3:
        insights.append({
            'type': 'info',
            'title': 'Building Momentum! ⚡',
            'message': f"You have a {metrics['study_streak']}-day streak. Try to extend it for better learning outcomes."
        })
    else:
        insights.append({
            'type': 'info',
            'title': 'Establish a Routine 📅',
            'message': "Regular practice is key. Try to take quizzes daily to build a study habit."
        })
    
    # Topic-specific insights
    if metrics['weaknesses']:
        insights.append({
            'type': 'warning',
            'title': 'Focus Areas Identified 🎯',
            'message': f"Consider spending extra time on: {', '.join(metrics['weaknesses'][:3])}"
        })
    
    if metrics['strengths']:
        insights.append({
            'type': 'success',
            'title': 'Your Strong Subjects 💪',
            'message': f"You excel in: {', '.join(metrics['strengths'][:3])}. Use this confidence to tackle harder topics!"
        })
    
    # Render insights
    for insight in insights:
        if insight['type'] == 'success':
            st.success(f"**{insight['title']}**\n\n{insight['message']}")
        elif insight['type'] == 'warning':
            st.warning(f"**{insight['title']}**\n\n{insight['message']}")
        else:
            st.info(f"**{insight['title']}**\n\n{insight['message']}")

@login_required
def performance_dashboard():
    """Enhanced Performance Dashboard with comprehensive analytics"""
    st.markdown(icon_text("chart", "Performance Analytics Dashboard", 24), unsafe_allow_html=True)
    
    # Check if user has any quiz data
    user_data = st.session_state.get('user_data', {})
    # Try both 'id' and '_id' field names for compatibility
    user_id = user_data.get('id') or user_data.get('_id') if user_data else None
    
    if not user_id:
        st.error("User session not found. Please log in again.")
        st.info("If you just logged in, try refreshing the page.")
        
        # Provide a way back to dashboard
        if st.button("🏠 Back to Dashboard"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
        return
    
    # Welcome message
    st.markdown(f"""
    <div style="
        background: linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h3 style="margin: 0; color: #e2e8f0;">
            {get_svg_icon('wave', 24, '#667eea')} Welcome back, {user_data.get('full_name', 'Student')}!
        </h3>
        <p style="margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.8);">
            Here's your comprehensive performance analysis and learning insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize analytics with error handling
    try:
        analytics = PerformanceAnalytics(user_id)
        metrics = analytics.calculate_performance_metrics()
        
        # Check if user has any quiz data
        if metrics['total_quizzes'] == 0:
            # Show welcome message for new users
            render_no_data_dashboard(user_data)
            return
        
        # Main metrics dashboard
        render_performance_metrics(metrics)
        
        st.markdown("---")
        
        # Charts and visualizations
        render_performance_charts(metrics)
        
        st.markdown("---")
        
        # Topic analysis
        render_topic_analysis(metrics)
        
        st.markdown("---")
        
        # Recent activity timeline
        render_recent_activity(metrics)
        
        st.markdown("---")
        
        # AI insights and recommendations
        render_ai_insights(metrics)
        
    except Exception as e:
        st.error(f"Error loading performance data: {str(e)}")
        st.info("This might be due to database connection issues or no quiz data available.")
        
        # Show fallback dashboard
        render_no_data_dashboard(user_data)
        return
    
    # Action buttons
    st.markdown("---")
    st.markdown(icon_text("rocket", "Quick Actions", 20), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"{get_svg_icon('quiz', 20)} Take New Quiz", use_container_width=True, type="primary"):
            st.session_state.current_page = "quiz"
            st.rerun()
    
    with col2:
        if st.button(f"{get_svg_icon('study', 20)} Study Plan", use_container_width=True, type="secondary"):
            st.session_state.current_page = "planner"
            st.rerun()
    
    with col3:
        if st.button(f"{get_svg_icon('refresh', 20)} Refresh Data", use_container_width=True, type="secondary"):
            st.rerun()

# Demo data function for testing without MongoDB
def render_demo_dashboard():
    """Render demo dashboard when no data is available"""
    st.markdown(icon_text("info", "Demo Performance Dashboard", 20), unsafe_allow_html=True)
    
    # Demo metrics
    demo_metrics = {
        'total_quizzes': 15,
        'accuracy_percentage': 78.5,
        'study_streak': 5,
        'total_questions': 150
    }
    
    render_performance_metrics(demo_metrics)
    
    st.info("""
    🚀 **This is a demo of your Performance Dashboard!**
    
    Once you complete quizzes, you'll see:
    - Real-time performance analytics
    - Interactive charts and trends
    - Topic-wise analysis
    - AI-powered insights and recommendations
    - Study streak tracking
    - Personalized improvement suggestions
    
    Take your first quiz to unlock the full dashboard experience!
    """)

def render_no_data_dashboard(user_data: Dict[str, Any]):
    """Render dashboard for users with no quiz data yet"""
    st.markdown("---")
    
    # Welcome message for new users
    st.markdown(f"""
    <div style="
        background: linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <h2 style="color: #e2e8f0; margin: 0 0 1rem 0;">
            🎯 Welcome to Your Learning Journey!
        </h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem; margin: 0;">
            Ready to unlock your potential, {user_data.get('full_name', 'Student')}?
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature preview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            color: white;
            margin: 1rem 0;
        ">
            <h3 style="margin: 0 0 0.5rem 0;">📊 Performance Analytics</h3>
            <p style="margin: 0; font-size: 0.9rem;">Track your progress with detailed charts and insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(45deg, #f093fb, #f5576c);
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            color: white;
            margin: 1rem 0;
        ">
            <h3 style="margin: 0 0 0.5rem 0;">🤖 AI Insights</h3>
            <p style="margin: 0; font-size: 0.9rem;">Get personalized recommendations and feedback</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            color: white;
            margin: 1rem 0;
        ">
            <h3 style="margin: 0 0 0.5rem 0;">🏆 Achievement Tracking</h3>
            <p style="margin: 0; font-size: 0.9rem;">Monitor your learning streaks and milestones</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started section
    st.markdown("---")
    st.markdown(icon_text("rocket", "Get Started", 20), unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        🚀 **Ready to begin your learning adventure?**
        
        Your performance dashboard will come alive with:
        - 📈 Real-time performance analytics
        - 🎯 Topic-wise progress tracking
        - 🧠 AI-powered learning insights
        - ⚡ Study streak monitoring
        - 🏅 Achievement badges and milestones
        
        **Take your first quiz to unlock the full dashboard experience!**
        """)
    
    with col2:
        if st.button("🎯 Take First Quiz", type="primary", use_container_width=True):
            st.session_state.current_page = 'quiz'
            st.rerun()
        
        if st.button("📚 View Study Planner", type="secondary", use_container_width=True):
            st.session_state.current_page = 'planner'
            st.rerun()
        
        st.metric("Ready to Start", "100%", "Let's go! 🚀")

if __name__ == "__main__":
    init_session_state()
    performance_dashboard()
