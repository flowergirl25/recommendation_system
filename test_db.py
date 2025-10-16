import pymysql
from app.config.db_connection import connecting_db

def test_connection():
    """Simple test to check if database connection works"""
    print("Testing database connection...")
    
    # Test connection
    conn = connecting_db()
    
    if conn:
        print(" Connection successful!")
        
        # Try a simple query
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f" Query test passed: {result}")
            cursor.close()
        except Exception as e:
            print(f" Query failed: {e}")
        
        # Close connection
        conn.close()
        print(" Connection closed")
        
    else:
        print(" Connection failed!")

# Run the test
if __name__ == "__main__":
    test_connection()