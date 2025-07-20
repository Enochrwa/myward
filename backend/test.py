from app.db.database import get_database_connection

def get_data(id: str):

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    # 1️⃣ Fetch the query image feature and category
    cursor.execute("SELECT * FROM images WHERE id = %s", (id,))
    data = cursor.fetchall()
    print(data)
   

get_data("0ae01b82-9285-4ed4-ae6f-98e49375e965")



