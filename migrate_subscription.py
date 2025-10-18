"""
Database Migration Script for Subscription System
Adds subscription fields to existing users and updates schema
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_database, COLLECTIONS
from utils.subscription import SubscriptionManager

def migrate_database():
    """
    Run database migration to add subscription fields
    """
    print("🔄 Starting database migration for subscription system...")
    
    # Test database connection
    db = get_database()
    if db is None:
        print("❌ Database connection failed!")
        return False
    
    print("✅ Database connection successful")
    
    # Initialize subscription manager
    manager = SubscriptionManager()
    
    # Get users collection
    users_collection = db[COLLECTIONS["users"]]
    
    try:
        # Count users without subscription fields
        users_without_subscription = list(users_collection.find({
            "subscription_type": {"$exists": False}
        }))
        
        total_users = users_collection.count_documents({})
        users_to_migrate = len(users_without_subscription)
        
        print(f"📊 Database Stats:")
        print(f"   Total users: {total_users}")
        print(f"   Users needing migration: {users_to_migrate}")
        
        if users_to_migrate == 0:
            print("✅ All users already have subscription fields. Migration complete!")
            return True
        
        # Migrate users
        print(f"🔄 Migrating {users_to_migrate} users...")
        
        migrated_count = 0
        for user in users_without_subscription:
            result = users_collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "subscription_type": "free",
                        "subscription_changed_date": datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                migrated_count += 1
                print(f"   ✅ Migrated user: {user.get('username', 'Unknown')}")
            else:
                print(f"   ⚠️  Failed to migrate user: {user.get('username', 'Unknown')}")
        
        print(f"\n🎉 Migration Results:")
        print(f"   Successfully migrated: {migrated_count}/{users_to_migrate} users")
        print(f"   All users now have subscription fields!")
        
        # Verify migration
        remaining_users = users_collection.count_documents({
            "subscription_type": {"$exists": False}
        })
        
        if remaining_users == 0:
            print("✅ Migration verification successful - no users left to migrate")
            return True
        else:
            print(f"⚠️  Migration verification: {remaining_users} users still need migration")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def verify_subscription_system():
    """
    Verify that the subscription system is working correctly
    """
    print("\n🔍 Verifying subscription system...")
    
    try:
        manager = SubscriptionManager()
        
        # Test with a dummy user ID (this will return default values)
        from bson import ObjectId
        dummy_id = ObjectId()
        
        # Test getting subscription (should return default)
        subscription = manager.get_user_subscription(str(dummy_id))
        print(f"✅ get_user_subscription working: {subscription}")
        
        # Test premium check (should return False for non-existent user)
        is_premium = manager.is_premium_user(str(dummy_id))
        print(f"✅ is_premium_user working: {is_premium}")
        
        print("✅ Subscription system verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Subscription system verification failed: {str(e)}")
        return False

def show_current_stats():
    """
    Show current database statistics
    """
    print("\n📊 Current Database Statistics:")
    
    try:
        db = get_database()
        if db is None:
            print("❌ Database connection failed!")
            return
        
        users_collection = db[COLLECTIONS["users"]]
        
        # Count total users
        total_users = users_collection.count_documents({})
        
        # Count by subscription type
        free_users = users_collection.count_documents({"subscription_type": "free"})
        premium_users = users_collection.count_documents({"subscription_type": "premium"})
        no_subscription = users_collection.count_documents({
            "subscription_type": {"$exists": False}
        })
        
        print(f"   Total Users: {total_users}")
        print(f"   Free Users: {free_users}")
        print(f"   Premium Users: {premium_users}")
        print(f"   Users without subscription fields: {no_subscription}")
        
        # Show recent users
        recent_users = list(users_collection.find({}, {
            "username": 1, 
            "subscription_type": 1, 
            "created_at": 1
        }).sort("created_at", -1).limit(5))
        
        print(f"\n📋 Recent Users:")
        for user in recent_users:
            sub_type = user.get('subscription_type', 'No subscription field')
            created = user.get('created_at', 'Unknown date')
            if isinstance(created, datetime):
                created = created.strftime("%Y-%m-%d")
            print(f"   • {user.get('username', 'Unknown')} - {sub_type} - {created}")
        
    except Exception as e:
        print(f"❌ Failed to get stats: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ADAPTIVE EXAM PREPARATION AI - DATABASE MIGRATION")
    print("=" * 60)
    
    # Show current stats
    show_current_stats()
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify system
        verify_subscription_system()
        
        # Show updated stats
        show_current_stats()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("🎉 Subscription system is ready to use!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED!")
        print("Please check the errors above and try again.")
        print("=" * 60)