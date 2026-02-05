from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timezone
import threading
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the frontend directory path
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

# Configuration
reminders = {}
reminder_id_counter = 1
reminder_threads = {}
DATA_FILE = os.path.join(os.path.dirname(__file__), 'reminders_data.json')

# ==================== Data Persistence ====================

def load_reminders():
    """Load reminders from persistent storage"""
    global reminders, reminder_id_counter
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                reminders = data.get('reminders', {})
                reminder_id_counter = data.get('id_counter', 1)
                logger.info(f"Loaded {len(reminders)} reminders from disk")
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
            reminders = {}
            reminder_id_counter = 1

def save_reminders():
    """Save reminders to persistent storage"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'reminders': reminders,
                'id_counter': reminder_id_counter
            }, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving reminders: {e}")

# ==================== Reminder Monitoring ====================

def monitor_reminder(reminder_id, reminder_time, title):
    """Monitor reminder and trigger alerts at appropriate times"""
    logger.info(f"Started monitoring reminder: {title}")
    
    while reminder_id in reminders and not reminders[reminder_id].get('completed'):
        try:
            now = datetime.now()
            reminder_dt = datetime.fromisoformat(reminder_time)
            time_diff = (reminder_dt - now).total_seconds()
            
            # Send alert when within 15-20 second window
            if -1 <= time_diff <= 20 and not reminders[reminder_id].get('alert_sent'):
                reminders[reminder_id]['alert_sent'] = True
                reminders[reminder_id]['alert_time'] = now.isoformat()
                save_reminders()
                logger.info(f"🔔 ALERT TRIGGERED: {title} (Time left: {time_diff:.1f}s)")
            
            # Mark as triggered when time passes
            elif time_diff < -1 and not reminders[reminder_id].get('triggered'):
                reminders[reminder_id]['triggered'] = True
                reminders[reminder_id]['trigger_time'] = now.isoformat()
                save_reminders()
                logger.info(f"⏰ REMINDER TIME: {title}")
            
            threading.Event().wait(0.5)  # Check every 500ms for accuracy
            
        except Exception as e:
            logger.error(f"Error monitoring reminder {reminder_id}: {e}")
            break

# ==================== API Routes ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'reminders_count': len(reminders)
    })

@app.route('/api/reminders', methods=['GET'])
def get_all_reminders():
    """Get all reminders"""
    try:
        reminders_list = list(reminders.values())
        reminders_list.sort(key=lambda x: x['time'])
        return jsonify(reminders_list)
    except Exception as e:
        logger.error(f"Error getting reminders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    """Create a new reminder"""
    global reminder_id_counter
    
    try:
        data = request.json
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        reminder_time = data.get('time')
        
        # Validation
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        if not reminder_time:
            return jsonify({'error': 'Time is required'}), 400
        
        # Validate datetime format
        try:
            datetime.fromisoformat(reminder_time)
        except ValueError:
            return jsonify({'error': 'Invalid datetime format'}), 400
        
        # Create reminder
        reminder_id = str(reminder_id_counter)
        reminder_id_counter += 1
        
        reminders[reminder_id] = {
            'id': reminder_id,
            'title': title,
            'description': description,
            'time': reminder_time,
            'created_at': datetime.now().isoformat(),
            'triggered': False,
            'alert_sent': False,
            'completed': False,
            'alert_time': None,
            'trigger_time': None
        }
        
        save_reminders()
        
        # Start monitoring thread
        thread = threading.Thread(
            target=monitor_reminder,
            args=(reminder_id, reminder_time, title),
            daemon=True
        )
        thread.start()
        reminder_threads[reminder_id] = thread
        
        logger.info(f"Created reminder: {title}")
        return jsonify(reminders[reminder_id]), 201
        
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<reminder_id>', methods=['GET'])
def get_reminder(reminder_id):
    """Get a specific reminder"""
    if reminder_id not in reminders:
        return jsonify({'error': 'Reminder not found'}), 404
    return jsonify(reminders[reminder_id])

@app.route('/api/reminders/<reminder_id>', methods=['PUT'])
def update_reminder(reminder_id):
    """Update a reminder"""
    if reminder_id not in reminders:
        return jsonify({'error': 'Reminder not found'}), 404
    
    try:
        data = request.json
        
        # Update allowed fields
        if 'title' in data:
            reminders[reminder_id]['title'] = data['title'].strip()
        if 'description' in data:
            reminders[reminder_id]['description'] = data['description'].strip()
        if 'time' in data:
            # Validate datetime
            datetime.fromisoformat(data['time'])
            reminders[reminder_id]['time'] = data['time']
            reminders[reminder_id]['alert_sent'] = False  # Reset alert flag
        
        reminders[reminder_id]['updated_at'] = datetime.now().isoformat()
        save_reminders()
        
        logger.info(f"Updated reminder: {reminder_id}")
        return jsonify(reminders[reminder_id])
        
    except ValueError:
        return jsonify({'error': 'Invalid datetime format'}), 400
    except Exception as e:
        logger.error(f"Error updating reminder: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    """Delete a reminder"""
    if reminder_id not in reminders:
        return jsonify({'error': 'Reminder not found'}), 404
    
    try:
        title = reminders[reminder_id]['title']
        del reminders[reminder_id]
        if reminder_id in reminder_threads:
            del reminder_threads[reminder_id]
        
        save_reminders()
        logger.info(f"Deleted reminder: {title}")
        
        return jsonify({'success': True, 'message': 'Reminder deleted'})
    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<reminder_id>/complete', methods=['POST'])
def mark_complete(reminder_id):
    """Mark a reminder as complete"""
    if reminder_id not in reminders:
        return jsonify({'error': 'Reminder not found'}), 404
    
    try:
        reminders[reminder_id]['completed'] = True
        reminders[reminder_id]['completed_at'] = datetime.now().isoformat()
        save_reminders()
        
        logger.info(f"Marked reminder complete: {reminders[reminder_id]['title']}")
        return jsonify(reminders[reminder_id])
        
    except Exception as e:
        logger.error(f"Error marking reminder complete: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-alerts', methods=['GET'])
def check_alerts():
    """Check for reminders that need alerts"""
    alerts = {}
    
    try:
        # Use UTC time for comparison since browser sends ISO format with Z
        now = datetime.now(timezone.utc)
        
        for rid, reminder in reminders.items():
            # Skip completed reminders
            if reminder.get('completed', False):
                continue
            
            # Skip if already alerted or triggered
            if reminder.get('alert_sent', False) or reminder.get('triggered', False):
                continue
            
            try:
                # Parse reminder time - handle both UTC and naive datetimes
                reminder_time_str = reminder['time']
                
                # If it ends with Z, it's UTC; otherwise treat as naive and add UTC
                if reminder_time_str.endswith('Z'):
                    reminder_dt = datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
                else:
                    # Try parsing ISO format
                    reminder_dt = datetime.fromisoformat(reminder_time_str)
                    # If naive, assume it's UTC
                    if reminder_dt.tzinfo is None:
                        reminder_dt = reminder_dt.replace(tzinfo=timezone.utc)
                
                time_diff = (reminder_dt - now).total_seconds()
                
                logger.info(f"Checking: {reminder['title']} | Time diff: {time_diff:.1f}s | Reminder: {reminder_time_str}")
                
                # Send alert within 15-20 second window (15 seconds BEFORE the reminder time)
                if -1 <= time_diff <= 20:
                    alerts[rid] = {
                        'type': 'alert' if time_diff > 0 else 'triggered',
                        'reminder': reminder,
                        'time_left': max(0, time_diff)
                    }
                    reminders[rid]['alert_sent'] = True
                    logger.info(f"🔔 ALERT QUEUED: {reminder['title']} ({time_diff:.1f}s left)")
                    
            except Exception as e:
                logger.error(f"Error processing reminder {rid}: {e}")
        
        if alerts:
            save_reminders()
            logger.info(f"Returning {len(alerts)} alerts")
        
        return jsonify(alerts)
        
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get app statistics"""
    try:
        completed = sum(1 for r in reminders.values() if r['completed'])
        upcoming = sum(1 for r in reminders.values() if not r['completed'])
        triggered = sum(1 for r in reminders.values() if r['triggered'])
        
        return jsonify({
            'total': len(reminders),
            'upcoming': upcoming,
            'completed': completed,
            'triggered': triggered
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== Error Handlers ====================

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.isfile(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)
    return send_from_directory(frontend_dir, 'index.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ==================== Startup ====================

if __name__ == '__main__':
    load_reminders()
    logger.info("🚀 Starting Reminder App Backend on http://0.0.0.0:3000")
    app.run(debug=True, port=3000, host='0.0.0.0')
