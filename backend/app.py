# 1. THIS MUST BE AT THE VERY TOP OF THE FILE
import gevent.monkey
gevent.monkey.patch_all()

# 2. Standard imports below
import os
import json
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# 3. Strengthened CORS for the REST API
CORS(app, resources={r"/*": {"origins": "*"}})

DB_HOST = os.environ.get("DB_HOST", "postgresql")
DB_NAME = os.environ.get("DB_NAME", "preptrackdb")
DB_USER = os.environ.get("DB_USER", "prepuser")
DB_PASS = os.environ.get("DB_PASS", "SuperSecret123")

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis-broker:6379/0")

# 4. Strengthened CORS for WebSockets
socketio = SocketIO(app, cors_allowed_origins="*", message_queue=REDIS_URL, async_mode='gevent')

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/messages', methods=['GET'])
def get_message_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username, text, parent_id, reactions FROM messages ORDER BY created_at ASC;')
        messages = [{"id": m[0], "username": m[1], "text": m[2], "parent_id": m[3], "reactions": m[4]} for m in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('send_message')
def handle_message(data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO messages (username, text, parent_id) VALUES (%s, %s, %s) RETURNING id;',
            (data['username'], data['text'], data.get('parent_id'))
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        data['id'] = new_id
        emit('receive_message', data, broadcast=True)
    except Exception as e:
        print(f"Error saving message: {e}")

@socketio.on('add_reaction')
def handle_reaction(data):
    try:
        msg_id = data['message_id']
        reaction = data['reaction']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT reactions FROM messages WHERE id = %s;', (msg_id,))
        result = cur.fetchone()
        reactions = result[0] if result and result[0] else {}
        
        reactions[reaction] = reactions.get(reaction, 0) + 1
        
        cur.execute('UPDATE messages SET reactions = %s WHERE id = %s;', (json.dumps(reactions), msg_id))
        conn.commit()
        cur.close()
        conn.close()

        emit('update_reaction', {'message_id': msg_id, 'reactions': reactions}, broadcast=True)
    except Exception as e:
        print(f"Error adding reaction: {e}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
