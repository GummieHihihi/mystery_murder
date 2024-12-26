import csv
import os
import time
from typing import List, Dict, Callable

class EventTrigger:
    def __init__(self):
        self.keyword_events: Dict[str, List[Dict]] = {}
        self.time_events: List[Dict] = []
        self.triggered_events: set = set()
        self.start_time = time.time()
        self.callbacks = {
            'reveal_secret': self.reveal_secret,
            'update_character': self.update_character,
            'add_evidence': self.add_evidence,
            'change_mood': self.change_mood
            # Thêm callbacks khác tại đây
        }

    def add_keyword_event(self, keyword: str, event_id: str, callback_name: str, event_data: Dict = None):
        """Add a new keyword-based event"""
        if keyword not in self.keyword_events:
            self.keyword_events[keyword] = []
        
        self.keyword_events[keyword].append({
            'id': event_id,
            'callback': self.callbacks[callback_name],
            'data': event_data
        })

    def add_time_event(self, minutes: float, event_id: str, callback_name: str, event_data: Dict = None):
        """Add a new time-based event"""
        self.time_events.append({
            'time': minutes * 60,  # Convert to seconds
            'id': event_id,
            'callback': self.callbacks[callback_name],
            'data': event_data,
            'triggered': False
        })

    # Callback functions
    def reveal_secret(self, character_id: int, event_data: Dict):
        """Reveal a secret to a character"""
        return {
            'type': 'reveal_info',
            'character_id': character_id,
            'content': event_data.get('content', '')
        }

    def update_character(self, character_id: int, event_data: Dict):
        """Update character sheet"""
        return {
            'type': 'update_character',
            'character_id': character_id,
            'sheet_name': event_data.get('sheet_name'),
            'append_only': event_data.get('append_only', True),
            'content': event_data.get('content', '')
        }

    def add_evidence(self, character_id: int, event_data: Dict):
        """Add new evidence"""
        return {
            'type': 'add_evidence',
            'character_id': character_id,
            'evidence': event_data.get('evidence', '')
        }

    def change_mood(self, character_id: int, event_data: Dict):
        """Change character's mood"""
        return {
            'type': 'change_mood',
            'character_id': character_id,
            'mood': event_data.get('mood', '')
        }

    def check_keyword(self, message: str) -> List[Dict]:
        """Check if message contains any trigger keywords"""
        triggered = []
        for keyword, events in self.keyword_events.items():
            if keyword.lower() in message.lower():
                for event in events:
                    if event['id'] not in self.triggered_events:
                        triggered.append({
                            'id': event['id'],
                            'callback': event['callback'],
                            'data': event['data']
                        })
                        self.triggered_events.add(event['id'])
        return triggered

    def check_time_events(self) -> List[Dict]:
        """Check if any time-based events should trigger"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        triggered = []
        
        for event in self.time_events:
            if not event['triggered'] and elapsed_time >= event['time']:
                event['triggered'] = True
                if event['id'] not in self.triggered_events:
                    triggered.append({
                        'id': event['id'],
                        'callback': event['callback'],
                        'data': event['data']
                    })
                    self.triggered_events.add(event['id'])
        return triggered

    def reset(self):
        """Reset all triggered events"""
        self.triggered_events.clear()
        self.start_time = time.time()
        for event in self.time_events:
            event['triggered'] = False

class EventManager:
    def __init__(self, conversation_history):
        self.conversation_history = conversation_history
        self.event_trigger = EventTrigger()
        self.base_path = "util/event_system"

    def load_event_sheet(self, filename: str):
        """Load events from CSV file"""
        filepath = os.path.join(self.base_path, "events", filename)
        
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    event_data = {
                        'sheet_name': row.get('sheet_name', ''),
                        'append_only': row.get('append_only', 'true').lower() == 'true',
                        'content': row.get('content', ''),
                        'evidence': row.get('evidence', ''),
                        'mood': row.get('mood', '')
                    }
                    
                    if row['trigger_type'] == 'keyword':
                        self.event_trigger.add_keyword_event(
                            keyword=row['trigger_value'],
                            event_id=row['event_id'],
                            callback_name=row['action'],
                            event_data=event_data
                        )
                    elif row['trigger_type'] == 'time':
                        self.event_trigger.add_time_event(
                            minutes=float(row['trigger_value']),
                            event_id=row['event_id'],
                            callback_name=row['action'],
                            event_data=event_data
                        )
        except FileNotFoundError:
            print(f"Warning: Event sheet {filename} not found in {filepath}")

    def load_character_sheet(self, character_id: int, sheet_name: str) -> List[Dict]:
        """Load new character sheet from event_system directory"""
        filepath = os.path.join(self.base_path, "character_sheets", sheet_name)
        character_data = []
        
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in reader:
                    if len(row) >= 2 and (len(row[0].strip()) > 0 or len(row[1].strip()) > 0):
                        character_data.append({
                            "role": "system",
                            "content": f"{row[0]}: {row[1]}"
                        })
            return character_data
        except FileNotFoundError:
            print(f"Warning: Character sheet {sheet_name} not found in {filepath}")
            return []

    def update_character_state(self, character_id: int, event_data: Dict):
        """Update character's state based on event data"""
        if 'sheet_name' in event_data and event_data['sheet_name']:
            new_character_data = self.load_character_sheet(character_id, event_data['sheet_name'])
            
            append_only = event_data.get('append_only', True)
            if not append_only:
                initial_prompts = [msg for msg in self.conversation_history[character_id] 
                                 if msg["role"] == "system" and "initial_prompt" in msg.get("metadata", {})]
                self.conversation_history[character_id] = initial_prompts
            
            self.conversation_history[character_id].extend(new_character_data)

        if 'content' in event_data and event_data['content']:
            self.conversation_history[character_id].append({
                "role": "system",
                "content": event_data['content']
            })

    def process_message(self, message: str, character_id: int):
        """Process incoming message and check for events"""
        # Check keyword triggers
        keyword_events = self.event_trigger.check_keyword(message)
        for event in keyword_events:
            event_data = event['callback'](character_id, event['data'])
            self.handle_triggered_event(event_data)

        # Check time triggers
        time_events = self.event_trigger.check_time_events()
        for event in time_events:
            event_data = event['callback'](character_id, event['data'])
            self.handle_triggered_event(event_data)

        return bool(keyword_events or time_events)

    def handle_triggered_event(self, event_data: Dict):
        """Process triggered event data"""
        event_type = event_data.get('type', '')
        character_id = int(event_data.get('character_id', 0))
        
        if event_type in ['update_character', 'reveal_info']:
            self.update_character_state(character_id, event_data)
        # Add more event type handlers as needed

    def create_event_system_structure(self):
        """Create the necessary directory structure for event system"""
        os.makedirs(os.path.join(self.base_path, "events"), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, "character_sheets"), exist_ok=True)