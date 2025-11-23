import os
import sys
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import necessary Flask components and services
from backend.app import app
from backend.services.reminder_service import check_and_trigger_reminders

def reminder_job():
    """The function that runs the reminder check within the Flask application context."""
    with app.app_context():
        # Get the current time and check for due reminders
        triggered_count = check_and_trigger_reminders()
        
        # Log the activity for debugging
        if triggered_count > 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] --- Scheduler: Triggered {triggered_count} reminder(s).")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] --- Scheduler: No reminders due.")


if __name__ == '__main__':
    # Initialize the scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule reminder_job to run every 60 seconds (1 minute)
    # This is the heartbeat of your Context-Aware Reminders system.
    scheduler.add_job(reminder_job, 'interval', seconds=60, id='reminder_check')
    
    print('Starting Reminder Scheduler...')
    scheduler.start()

    # Keep the main thread alive, so the scheduler can run in the background
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Shut down the scheduler cleanly when interrupted
        scheduler.shutdown()
        print('Scheduler stopped.')