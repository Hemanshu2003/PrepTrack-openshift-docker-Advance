import os
import json
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get("DB_HOST", "postgresql")
DB_NAME = os.environ.get("DB_NAME", "preptrackdb")
DB_USER = os.environ.get("DB_USER", "prepuser")
DB_PASS = os.environ.get("DB_PASS", "SuperSecret123")

# Redis configuration for OpenShift scaling
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
socketio = SocketIO(app, cors_allowed_origins="*", message_queue=REDIS_URL, async_mode='gevent')

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route('/api/messages', methods=['GET'])
def get_message_history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, text, parent_id, reactions FROM messages ORDER BY created_at ASC;')
    messages = [{"id": m[0], "username": m[1], "text": m[2], "parent_id": m[3], "reactions": m[4]} for m in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(messages)

# WebSocket Event: New Message
@socketio.on('send_message')
def handle_message(data):
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
    # Broadcast to all connected clients across all OpenShift pods
    emit('receive_message', data, broadcast=True)

# WebSocket Event: Add Reaction
@socketio.on('add_reaction')
def handle_reaction(data):
    msg_id = data['message_id']
    reaction = data['reaction'] # e.g., "👍"
    
    conn = get_db_connection()
    cur = conn.cursor()
    # Fetch current reactions, update the count, save back to JSONB
    cur.execute('SELECT reactions FROM messages WHERE id = %s;', (msg_id,))
    reactions = cur.fetchone()[0] or {}
    reactions[reaction] = reactions.get(reaction, 0) + 1
    
    cur.execute('UPDATE messages SET reactions = %s WHERE id = %s;', (json.dumps(reactions), msg_id))
    conn.commit()
    cur.close()
    conn.close()

    emit('update_reaction', {'message_id': msg_id, 'reactions': reactions}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
