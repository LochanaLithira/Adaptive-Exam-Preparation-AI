import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import streamlit as st
from bson import ObjectId

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_database, COLLECTIONS

class SubscriptionManager:
    """Manages user subscriptions and feature access"""
    
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db[COLLECTIONS["users"]] if self.db is not None else None
    
    def get_user_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current subscription details
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Dict with subscription details: {
                'subscription_type': 'free' | 'premium',
                'subscription_changed_date': datetime,
                'is_premium': bool
            }
        """
        if self.users_collection is None:
            return {
                'subscription_type': 'free',
                'subscription_changed_date': None,
                'is_premium': False
            }
        
        try:
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user = self.users_collection.find_one({"_id": user_id})
            
            if not user:
                return {
                    'subscription_type': 'free',
                    'subscription_changed_date': None,
                    'is_premium': False
                }
            
            # Get subscription details with fallback to 'free'
            subscription_type = user.get('subscription_type', 'free')
            subscription_changed_date = user.get('subscription_changed_date')
            
            return {
                'subscription_type': subscription_type,
                'subscription_changed_date': subscription_changed_date,
                'is_premium': subscription_type == 'premium'
            }
            
        except Exception as e:
            st.error(f"Error getting subscription status: {str(e)}")
            return {
                'subscription_type': 'free',
                'subscription_changed_date': None,
                'is_premium': False
            }
    
    def update_subscription(self, user_id: str, subscription_type: str) -> Tuple[bool, str]:
        """
        Update user's subscription type
        
        Args:
            user_id: User's unique identifier
            subscription_type: 'free' or 'premium'
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.users_collection is None:
            return False, "Database connection failed"
        
        if subscription_type not in ['free', 'premium']:
            return False, "Invalid subscription type"
        
        try:
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Update user subscription
            result = self.users_collection.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "subscription_type": subscription_type,
                        "subscription_changed_date": datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                return True, f"Successfully updated to {subscription_type} plan"
            else:
                return False, "No changes made to subscription"
                
        except Exception as e:
            return False, f"Error updating subscription: {str(e)}"
    
    def is_premium_user(self, user_id: str) -> bool:
        """
        Check if user has premium subscription
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user is premium, False otherwise
        """
        subscription = self.get_user_subscription(user_id)
        return subscription['is_premium']

# ==============================
# Convenience Functions
# ==============================

def get_current_user_subscription() -> Dict[str, Any]:
    """
    Get current logged-in user's subscription details from session state
    
    Returns:
        Dict with subscription details or default free subscription
    """
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id') or user_data.get('id')
    
    if not user_id:
        return {
            'subscription_type': 'free',
            'subscription_changed_date': None,
            'is_premium': False
        }
    
    manager = SubscriptionManager()
    return manager.get_user_subscription(user_id)

def is_current_user_premium() -> bool:
    """
    Check if current logged-in user has premium subscription
    
    Returns:
        True if current user is premium, False otherwise
    """
    subscription = get_current_user_subscription()
    return subscription['is_premium']

def update_current_user_subscription(subscription_type: str) -> Tuple[bool, str]:
    """
    Update current logged-in user's subscription
    
    Args:
        subscription_type: 'free' or 'premium'
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('_id') or user_data.get('id')
    
    if not user_id:
        return False, "User not logged in"
    
    manager = SubscriptionManager()
    success, message = manager.update_subscription(user_id, subscription_type)
    
    # Update session state if successful
    if success and 'user_data' in st.session_state:
        st.session_state.user_data['subscription_type'] = subscription_type
        st.session_state.user_data['subscription_changed_date'] = datetime.now()
    
    return success, message

def initialize_all_users_subscription():
    """
    Initialize subscription fields for all existing users who don't have them
    This is a one-time migration function
    """
    db = get_database()
    if db is None:
        st.error("Database connection failed")
        return False
    
    users_collection = db[COLLECTIONS["users"]]
    
    try:
        # Find users without subscription_type field
        users_without_subscription = users_collection.find({
            "subscription_type": {"$exists": False}
        })
        
        count = 0
        for user in users_without_subscription:
            users_collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "subscription_type": "free",
                        "subscription_changed_date": datetime.now()
                    }
                }
            )
            count += 1
        
        return count
        
    except Exception as e:
        st.error(f"Error initializing user subscriptions: {str(e)}")
        return False
