// Configuration
const API_BASE_URL = 'http://localhost:3000/api';
const ALERT_CHECK_INTERVAL = 500; // Check every 500ms for better accuracy

// State
let reminders = [];
let alertCheckInterval;
let currentAlertReminder = null;
let timerInterval = null;

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Reminder App...');
    setupFormHandler();
    loadReminders();
    startAlertChecker();
    setMinDateTime();
    updateStats();
});

// Set minimum datetime to now
function setMinDateTime() {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('reminderTime').min = now.toISOString().slice(0, 16);
}

// ==================== Form Handler ====================

function setupFormHandler() {
    document.getElementById('reminderForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const title = document.getElementById('title').value.trim();
        const description = document.getElementById('description').value.trim();
        const time = document.getElementById('reminderTime').value;
        
        if (!title || !time) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        try {
            const reminderDateTime = new Date(time).toISOString();
            
            const response = await fetch(`${API_BASE_URL}/reminders`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, time: reminderDateTime })
            });
            
            if (response.ok) {
                document.getElementById('reminderForm').reset();
                setMinDateTime();
                await loadReminders();
                updateStats();
                showNotification('✓ Reminder created successfully!', 'success');
            } else {
                const error = await response.json();
                showNotification(`Error: ${error.error}`, 'error');
            }
        } catch (error) {
            console.error('Error creating reminder:', error);
            showNotification('Error creating reminder', 'error');
        }
    });
}

// ==================== Data Loading ====================

async function loadReminders() {
    try {
        const response = await fetch(`${API_BASE_URL}/reminders`);
        if (response.ok) {
            reminders = await response.json();
            renderReminders();
            console.log(`Loaded ${reminders.length} reminders`);
        }
    } catch (error) {
        console.error('Error loading reminders:', error);
    }
}

// ==================== Rendering ====================

function renderReminders() {
    const remindersList = document.getElementById('remindersList');
    
    if (reminders.length === 0) {
        remindersList.innerHTML = '<p class="empty-state">No reminders yet. Create one to get started!</p>';
        return;
    }
    
    // Sort by time
    const sorted = [...reminders].sort((a, b) => new Date(a.time) - new Date(b.time));
    
    remindersList.innerHTML = sorted.map(reminder => {
        const reminderTime = new Date(reminder.time);
        const now = new Date();
        const timeLeft = reminderTime - now;
        const isCompleted = reminder.completed;
        
        let timeDisplay = formatDateTime(reminderTime);
        let timeLeftDisplay = '';
        
        if (!isCompleted) {
            if (timeLeft > 0) {
                timeLeftDisplay = `<span class="reminder-time-left">${formatTimeLeft(timeLeft)}</span>`;
            } else {
                timeLeftDisplay = `<span class="reminder-time-left overdue">OVERDUE</span>`;
            }
        }
        
        return `
            <div class="reminder-card ${isCompleted ? 'completed' : ''}">
                <h3 class="reminder-title">${escapeHtml(reminder.title)}</h3>
                ${reminder.description ? `<p class="reminder-description">${escapeHtml(reminder.description)}</p>` : ''}
                <div class="reminder-time">${timeDisplay}</div>
                ${timeLeftDisplay}
                <div class="reminder-actions">
                    ${!isCompleted ? `<button class="btn btn-complete" onclick="completeReminder('${reminder.id}')">Mark Done</button>` : ''}
                    <button class="btn btn-danger" onclick="deleteReminder('${reminder.id}')">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

// ==================== Time Formatting ====================

function formatDateTime(date) {
    return date.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function formatTimeLeft(ms) {
    const seconds = Math.floor(ms / 1000);
    
    if (seconds < 60) {
        return `${seconds}s left`;
    }
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) {
        return `${minutes}m left`;
    }
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
        return `${hours}h left`;
    }
    
    const days = Math.floor(hours / 24);
    return `${days}d left`;
}

// ==================== Alert System ====================

function startAlertChecker() {
    alertCheckInterval = setInterval(checkForAlerts, ALERT_CHECK_INTERVAL);
    console.log('Alert checker started');
}

async function checkForAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/check-alerts`);
        if (response.ok) {
            const alerts = await response.json();
            
            if (Object.keys(alerts).length > 0) {
                console.log('🔔 Alerts found:', alerts);
                for (const [reminderId, alert] of Object.entries(alerts)) {
                    // Only trigger if there isn't already an alert showing
                    if (!currentAlertReminder || currentAlertReminder.id !== alert.reminder.id) {
                        console.log('Triggering alert for:', alert.reminder.title);
                        triggerAlert(alert);
                    }
                }
                // Reload reminders after alerts
                setTimeout(() => loadReminders(), 500);
            }
        }
    } catch (error) {
        console.error('Error checking alerts:', error);
    }
}

function triggerAlert(alert) {
    const { reminder, time_left, type } = alert;
    
    if (type === 'alert' || type === 'triggered') {
        currentAlertReminder = reminder;
        showAlertModal(reminder, Math.ceil(time_left));
    }
}

function showAlertModal(reminder, secondsLeft) {
    const modal = document.getElementById('alertModal');
    const title = document.getElementById('alertTitle');
    const description = document.getElementById('alertDescription');
    
    title.textContent = reminder.title;
    description.textContent = reminder.description || 'Your reminder time is here!';
    
    modal.classList.remove('hidden');
    playBeepSound();
    
    // Pulse animation
    const modalContent = modal.querySelector('.modal-content');
    modalContent.classList.add('alert-pulse');
    
    // Start timer display
    startTimerDisplay(secondsLeft);
}

function startTimerDisplay(initialSeconds) {
    if (timerInterval) clearInterval(timerInterval);
    
    let remaining = Math.max(0, initialSeconds);
    
    const update = () => {
        const timerDisplay = document.getElementById('timerDisplay');
        if (timerDisplay) {
            timerDisplay.textContent = `${Math.max(0, remaining)}s`;
        }
        remaining--;
        
        if (remaining < 0) {
            clearInterval(timerInterval);
        }
    };
    
    update();
    timerInterval = setInterval(update, 1000);
}

// ==================== Sound Alert ====================

function playBeepSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const now = audioContext.currentTime;
        const beepDuration = 0.15;
        const pauseDuration = 0.1;
        
        // Three ascending beeps
        playBeep(audioContext, now, 800, beepDuration);
        playBeep(audioContext, now + beepDuration + pauseDuration, 900, beepDuration);
        playBeep(audioContext, now + (beepDuration + pauseDuration) * 2, 1000, beepDuration);
        
        console.log('🔊 Beep sound played');
    } catch (error) {
        console.error('Error playing beep:', error);
    }
}

function playBeep(audioContext, startTime, frequency, duration) {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = frequency;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0, startTime);
    gainNode.gain.linearRampToValueAtTime(0.4, startTime + 0.05);
    gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + duration);
    
    oscillator.start(startTime);
    oscillator.stop(startTime + duration);
}

// ==================== Modal Actions ====================

function dismissAlert() {
    const modal = document.getElementById('alertModal');
    modal.classList.add('hidden');
    const modalContent = modal.querySelector('.modal-content');
    if (modalContent) {
        modalContent.classList.remove('alert-pulse');
    }
    currentAlertReminder = null;
    if (timerInterval) clearInterval(timerInterval);
    console.log('Alert dismissed');
}

async function markComplete() {
    if (!currentAlertReminder) return;
    
    try {
        await fetch(`${API_BASE_URL}/reminders/${currentAlertReminder.id}/complete`, {
            method: 'POST'
        });
        
        dismissAlert();
        await loadReminders();
        updateStats();
        showNotification('✓ Reminder marked as done!', 'success');
    } catch (error) {
        console.error('Error marking complete:', error);
        showNotification('Error updating reminder', 'error');
    }
}

async function completeReminder(reminderId) {
    try {
        await fetch(`${API_BASE_URL}/reminders/${reminderId}/complete`, {
            method: 'POST'
        });
        
        await loadReminders();
        updateStats();
        showNotification('✓ Reminder marked as done!', 'success');
    } catch (error) {
        console.error('Error completing reminder:', error);
        showNotification('Error updating reminder', 'error');
    }
}

async function deleteReminder(reminderId) {
    if (!confirm('Delete this reminder?')) return;
    
    try {
        await fetch(`${API_BASE_URL}/reminders/${reminderId}`, {
            method: 'DELETE'
        });
        
        await loadReminders();
        updateStats();
        showNotification('✓ Reminder deleted', 'success');
    } catch (error) {
        console.error('Error deleting reminder:', error);
        showNotification('Error deleting reminder', 'error');
    }
}

// ==================== Stats ====================

async function updateStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalReminders').textContent = stats.total;
            document.getElementById('upcomingReminders').textContent = stats.upcoming;
            document.getElementById('completedReminders').textContent = stats.completed;
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// ==================== Utilities ====================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 16px 24px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 2000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

console.log('✅ Reminder App loaded successfully');
