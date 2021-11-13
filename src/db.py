def create_table(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS chats (id INTEGER, odd_week TEXT, even_week TEXT)")

def select_odd_week(cursor):
    ans = cursor.execute("SELECT id, odd_week FROM chats").fetchall()
    return ans

def select_even_week(cursor):
    ans = cursor.execute("SELECT id, even_week FROM chats").fetchall()
    return ans

def select_id_where(cursor, chat_id):
    id = cursor.execute("SELECT id FROM chats WHERE id = ?", (chat_id,),).fetchone()
    return id

def insert(cursor, chat_id, name_odd, name_even):
    cursor.execute("INSERT INTO chats VALUES (?, ?, ?)", (chat_id, name_odd, name_even))

def update(cursor, name_odd, name_even, chat_id):
    cursor.execute("UPDATE chats SET odd_week = ?, even_week = ? WHERE id = ?", (name_odd, name_even, chat_id))
