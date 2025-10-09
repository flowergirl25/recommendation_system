import pymysql

def connecting_db():

    """DB connection setup"""

    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",         
            password="root",     
            database="movie_recommendation_db",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn

    except Exception as e:
        print(" Database connection failed:", e)
        return None
 