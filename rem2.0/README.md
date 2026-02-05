# 🚀 Reminder Pro - Professional Reminder Application

A production-grade reminder application with real-time alerts, beep notifications, and a modern responsive UI.

## ✨ Features

### Core Features
- ✅ **Create, Read, Update, Delete** reminders
- ✅ **Schedule reminders** for specific dates and times
- ✅ **Message Alert** - Modal popup with reminder details
- ✅ **Beep Sound Alert** - 3 ascending tones (800Hz, 900Hz, 1000Hz)
- ✅ **15-Second Advance Notice** - Alert triggers 15 seconds before reminder time
- ✅ **Real-time Countdown** - Shows seconds remaining
- ✅ **Persistent Storage** - Reminders saved to disk
- ✅ **Statistics Dashboard** - Track total, upcoming, and completed reminders

### Technical Excellence
- 🏗️ **Clean Architecture** - Separation of concerns
- 🔒 **Error Handling** - Comprehensive try-catch and validation
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Modern UI** - Gradient backgrounds, smooth animations
- 🔄 **Real-time Sync** - Frontend and backend stay synchronized
- 📊 **Logging** - Full debug logging on backend

## 🛠️ Tech Stack

**Backend:**
- Python 3.7+
- Flask (REST API)
- Flask-CORS (Cross-origin requests)
- Threading (Background monitoring)

**Frontend:**
- HTML5
- CSS3 (Grid, Flexbox, Gradients)
- Vanilla JavaScript (ES6+)
- Web Audio API (Sound alerts)

## 🚀 Quick Start

### Windows
```bash
# Double-click
start.bat
```

### macOS/Linux
```bash
# Make executable
chmod +x start.sh

# Run
./start.sh
```

### Manual Setup
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Terminal 1 - Start backend
python app.py

# Terminal 2 - Start backend is already running
# Navigate to http://localhost:3000
```

## 📋 How to Use

1. **Create a Reminder**
   - Enter title (required)
   - Add description (optional)
   - Select date and time
   - Click "Add Reminder"

2. **Get Alerted**
   - 15 seconds before reminder time:
     - 🔔 Modal popup appears
     - 🔊 Three beep sounds play
     - ⏱️ Countdown timer shows seconds left

3. **Manage Reminders**
   - View all upcoming reminders
   - See time remaining for each
   - Mark reminders as done
   - Delete reminders

## 🔌 API Endpoints

### Reminders
- `GET /api/reminders` - Get all reminders
- `POST /api/reminders` - Create reminder
- `GET /api/reminders/<id>` - Get specific reminder
- `PUT /api/reminders/<id>` - Update reminder
- `DELETE /api/reminders/<id>` - Delete reminder
- `POST /api/reminders/<id>/complete` - Mark complete

### System
- `GET /api/check-alerts` - Check for alerts (called by frontend)
- `GET /api/stats` - Get statistics
- `GET /api/health` - Health check

## 📁 Project Structure

```
rem2.0/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── requirements.txt       # Python dependencies
│   └── reminders_data.json   # Data persistence
├── frontend/
│   ├── index.html            # Main UI
│   └── assets/
│       ├── style.css         # Styling
│       └── script.js         # Client logic
├── start.bat                 # Windows launcher
├── start.sh                  # Unix launcher
└── README.md                 # This file
```

## 🎯 Configuration

### Backend (app.py)
- Port: 3000
- Host: 0.0.0.0
- Data file: `reminders_data.json`
- Alert window: 15-20 seconds

### Frontend (script.js)
- API URL: `http://localhost:3000/api`
- Alert check interval: 500ms

## 🔊 Sound Alert Details

Three ascending beep frequencies:
- Beep 1: 800Hz
- Beep 2: 900Hz
- Beep 3: 1000Hz

Duration: ~500ms total

## 🐛 Troubleshooting

**Backend won't start:**
- Check if port 3000 is available
- Ensure Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Frontend not loading:**
- Check if backend is running
- Verify port 8000 is available
- Clear browser cache (Ctrl+F5)
- Check browser console (F12) for errors

**No beep sound:**
- Check browser volume settings
- Allow browser to play audio
- Check browser console for errors
- Some browsers require user interaction

**Reminders not alerting:**
- Open browser console (F12)
- Look for `[ALERT]` logs
- Verify backend logs show monitoring
- Check if reminder time is in future

## 📝 Example Workflow

1. Create reminder: "Team Meeting"
   - Title: Team Meeting
   - Description: Discuss Q1 goals
   - Time: 2026-01-24 10:30

2. 10:15 (15 seconds before):
   - Modal pops up
   - Beep sound plays
   - Countdown shows: "15s"

3. User can:
   - Dismiss alert
   - Mark as done

4. Completed reminder saved to disk

## 🔒 Data Persistence

All reminders are automatically saved to `reminders_data.json`:
```json
{
  "reminders": {
    "1": {
      "id": "1",
      "title": "Meeting",
      "description": "Team sync",
      "time": "2026-01-24T10:30:00",
      "completed": false,
      ...
    }
  },
  "id_counter": 2
}
```

## 🎓 Code Quality

- ✅ Comprehensive error handling
- ✅ Input validation
- ✅ Logging throughout
- ✅ Clean code structure
- ✅ Comments and documentation
- ✅ Responsive design
- ✅ Accessibility considerations

## 📄 License

Educational project - MIT License

## 👨‍💻 Author

Created as a professional reminder application with enterprise-grade code quality.

---

**Made with ❤️ using Python, Flask, HTML, CSS, and JavaScript**

Enjoy staying organized! 📅
