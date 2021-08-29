# Scripts for accessing the user database

# Keeping here in-case switch is made from Repl DB to local MySQL DB. 

ADD_USER_SCRIPT = """
INSERT INTO server_list
(server_id, user_id, experience, lvl , last_message )
VALUES (%s, %s, %s, %s, %s);
"""
ADD_XP_SCRIPT = """
UPDATE server_list SET experience = experience + %s WHERE server_id = %s AND user_id = %s;
"""
CHECK_USER_LAST_MSG_EXISTS_SCRIPT = """
SELECT last_message FROM server_list WHERE server_id = %s AND user_id = %s;
"""
CHECK_USER_EXISTS_SCRIPT = """
SELECT * FROM server_list WHERE server_id = %s AND user_id = %s;
"""
GET_USER_STATS_SCRIPT = """
SELECT experience, lvl FROM server_list WHERE server_id = %s AND
user_id = %s
"""
GET_XP_SCRIPT = """
SELECT experience FROM server_list WHERE server_id = %s AND user_id = %s;
"""
UPDATE_LAST_MSG_SCRIPT = """
UPDATE server_list SET last_message = %s WHERE server_id = %s AND user_id = %s;
"""
UPDATE_LVL_SCRIPT = """
UPDATE server_list SET lvl = %s WHERE server_id = %s AND user_id = %s
"""