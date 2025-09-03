# agents/planner_agent.py

class PlannerAgent:
    def __init__(self, performance_data=None):
        """
        Accept performance_data as a dictionary.
        If None, use default sample data.
        """
        if performance_data:
            self.performance_data = performance_data
        else:
            # default sample data if no input
            self.performance_data = {
                "Math": {"score": 60, "weak": True},
                "Science": {"score": 85, "weak": False},
                "History": {"score": 50, "weak": True},
                "English": {"score": 75, "weak": False},
            }

    def generate_plan(self):
        study_plan = []
        for subject, stats in self.performance_data.items():
            study_plan.append({
                "subject": subject,
                "focus": "High" if stats["weak"] else "Low",
                "hours_per_week": 5 if stats["weak"] else 2,
                "recommendation": f"Practice extra exercises in {subject}" if stats["weak"] else f"Quick revision in {subject}"
            })
        return study_plan

