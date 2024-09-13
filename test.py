import win32evtlog
import win32api
import win32con

def read_event_logs():
    server = 'localhost'
    log_type = 'System'
    try:
        # Open the event log
        log_handle = win32evtlog.OpenEventLog(server, log_type)
        
        # Read the event log records
        events = win32evtlog.ReadEventLog(log_handle, win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ, 0)
        
        for event in events:
            # Event ID and source code
            event_id = event.EventID & 0xFFFF
            source = event.SourceName
            message = win32api.FormatMessage(event.EventCategory)
            
            # Check for shutdown and restart events
            if event_id in [6006, 6008, 6005, 6009]:  # Typical Event IDs for shutdown/restart
                print(f"Event ID: {event_id}")
                print(f"Source: {source}")
                print(f"Message: {message}")
                print("-" * 40)
                
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
read_event_logs()
