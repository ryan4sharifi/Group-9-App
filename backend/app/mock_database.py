
from datetime import datetime, date
from typing import Dict, List, Any, Optional



# In-memory storage dictionaries
MOCK_USERS: Dict[str, Dict] = {}
MOCK_PROFILES: Dict[str, Dict] = {}
MOCK_EVENTS: Dict[str, Dict] = {}
MOCK_NOTIFICATIONS: Dict[str, Dict] = {}
MOCK_HISTORY: Dict[str, Dict] = {}
MOCK_CONTACT_MESSAGES: List[Dict] = []

# SAMPLE HARDCODED DATA


SAMPLE_USERS = {
    "admin-001": {
        "id": "admin-001",
        "email": "admin@volunteer.org",
        "password": "$2b$12$nyZxynT8ZKXcyRIx6SoxCeim/W7nhGN4YSCQRkMxTi8C5JdElJ15e",  # "admin123"
        "role": "admin",
        "created_at": "2024-01-01T00:00:00"
    },
    "volunteer-001": {
        "id": "volunteer-001", 
        "email": "john.doe@email.com",
        "password": "$2b$12$poCKlqemOmXVCHsWE7ETjOXEzEfehxiTk3a/0xUNxfLuAjhkMYoqe",  # "volunteer123"
        "role": "volunteer",
        "created_at": "2024-01-15T00:00:00"
    },
    "volunteer-002": {
        "id": "volunteer-002",
        "email": "sarah.smith@email.com", 
        "password": "$2b$12$poCKlqemOmXVCHsWE7ETjOXEzEfehxiTk3a/0xUNxfLuAjhkMYoqe",  # "volunteer123"
        "role": "volunteer",
        "created_at": "2024-02-01T00:00:00"
    }
}

SAMPLE_PROFILES = {
    "volunteer-001": {
        "user_id": "volunteer-001",
        "full_name": "John Doe",
        "address1": "123 Main Street",
        "address2": "Apt 4B",
        "city": "Houston", 
        "state": "TX",
        "zip_code": "77001",
        "skills": ["Environmental Cleanup", "Event Planning", "Teaching"],
        "preferences": "Weekend events preferred, outdoor activities",
        "availability": "2024-12-01",
        "role": "volunteer"
    },
    "volunteer-002": {
        "user_id": "volunteer-002",
        "full_name": "Sarah Smith",
        "address1": "456 Oak Avenue",
        "address2": "",
        "city": "Austin",
        "state": "TX", 
        "zip_code": "78701",
        "skills": ["Customer Service", "Organization", "Food Service"],
        "preferences": "Indoor activities, flexible schedule",
        "availability": "2024-11-15",
        "role": "volunteer"
    }
}

SAMPLE_EVENTS = {
    "event-001": {
        "id": "event-001",
        "name": "Beach Cleanup Drive",
        "description": "Join us for a community beach cleanup to protect our marine environment and keep our beaches beautiful.",
        "location": "Galveston Beach State Park, TX",
        "required_skills": ["Environmental Cleanup", "Physical Work"],
        "urgency": "High",
        "event_date": "2024-12-15",
        "created_at": "2024-11-01T00:00:00"
    },
    "event-002": {
        "id": "event-002", 
        "name": "Food Bank Volunteer Day",
        "description": "Help sort, pack, and distribute food to families in need in our community.",
        "location": "Houston Food Bank, 535 Portwall St, Houston, TX",
        "required_skills": ["Organization", "Customer Service", "Food Service"],
        "urgency": "Medium",
        "event_date": "2024-12-20",
        "created_at": "2024-11-05T00:00:00"
    },
    "event-003": {
        "id": "event-003",
        "name": "Community Teaching Workshop", 
        "description": "Teach basic computer skills to seniors in our community center.",
        "location": "Community Center, 789 Elm St, Houston, TX",
        "required_skills": ["Teaching", "Technology", "Patience"],
        "urgency": "Low",
        "event_date": "2024-12-25",
        "created_at": "2024-11-10T00:00:00"
    }
}

SAMPLE_NOTIFICATIONS = {
    "notif-001": {
        "id": "notif-001",
        "user_id": "volunteer-001",
        "message": "You have been matched to 'Beach Cleanup Drive' based on your skills!",
        "is_read": False,
        "type": "match",
        "event_id": "event-001",
        "created_at": "2024-11-12T10:30:00"
    },
    "notif-002": {
        "id": "notif-002",
        "user_id": "volunteer-002", 
        "message": "You have been matched to 'Food Bank Volunteer Day' based on your skills!",
        "is_read": False,
        "type": "match",
        "event_id": "event-002", 
        "created_at": "2024-11-12T11:00:00"
    },
    "notif-003": {
        "id": "notif-003",
        "user_id": "volunteer-001",
        "message": "Reminder: 'Beach Cleanup Drive' is tomorrow! Don't forget to bring gloves.",
        "is_read": True,
        "type": "reminder", 
        "event_id": "event-001",
        "created_at": "2024-11-14T09:00:00"
    }
}

SAMPLE_HISTORY = {
    "history-001": {
        "id": "history-001",
        "user_id": "volunteer-001",
        "event_id": "event-001", 
        "status": "Signed Up",
        "created_at": "2024-11-12T15:00:00"
    },
    "history-002": {
        "id": "history-002", 
        "user_id": "volunteer-002",
        "event_id": "event-002",
        "status": "Attended",
        "created_at": "2024-11-01T14:30:00"
    }
}

# ================================
# MOCK DATABASE OPERATIONS
# ================================

def initialize_mock_data():
    """Initialize all mock data - call this when app starts"""
    global MOCK_USERS, MOCK_PROFILES, MOCK_EVENTS, MOCK_NOTIFICATIONS, MOCK_HISTORY
    
    MOCK_USERS.update(SAMPLE_USERS)
    MOCK_PROFILES.update(SAMPLE_PROFILES) 
    MOCK_EVENTS.update(SAMPLE_EVENTS)
    MOCK_NOTIFICATIONS.update(SAMPLE_NOTIFICATIONS)
    MOCK_HISTORY.update(SAMPLE_HISTORY)
    
    print("✅ Mock data initialized successfully")

def generate_id() -> str:
    """Generate a unique ID for new records"""
    return str(uuid.uuid4())

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

# ================================
# MOCK SUPABASE CLIENT
# ================================

class MockSupabaseResponse:
    """Mock response object that mimics Supabase response structure"""
    
    def __init__(self, data: Any = None, error: Any = None):
        self.data = data
        self.error = error

class MockSupabaseTable:
    """Mock Supabase table operations"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._storage_map = {
            "user_credentials": MOCK_USERS,
            "user_profiles": MOCK_PROFILES, 
            "events": MOCK_EVENTS,
            "notifications": MOCK_NOTIFICATIONS,
            "volunteer_history": MOCK_HISTORY
        }
    
    def select(self, columns: str = "*"):
        """Mock select operation"""
        return MockSupabaseQuery(self.table_name, self._storage_map.get(self.table_name, {}), "select", columns=columns)
    
    def insert(self, data: Dict):
        """Mock insert operation"""
        return MockSupabaseQuery(self.table_name, self._storage_map.get(self.table_name, {}), "insert", data=data)
    
    def update(self, data: Dict):
        """Mock update operation"""
        return MockSupabaseQuery(self.table_name, self._storage_map.get(self.table_name, {}), "update", data=data)
    
    def delete(self):
        """Mock delete operation"""
        return MockSupabaseQuery(self.table_name, self._storage_map.get(self.table_name, {}), "delete")
    
    def upsert(self, data: Dict, on_conflict: List[str] = None):
        """Mock upsert operation"""
        return MockSupabaseQuery(self.table_name, self._storage_map.get(self.table_name, {}), "upsert", data=data, on_conflict=on_conflict)

class MockSupabaseQuery:
    """Mock Supabase query builder"""
    
    def __init__(self, table_name: str, storage: Dict, operation: str, columns: str = "*", data: Dict = None, on_conflict: List[str] = None):
        self.table_name = table_name
        self.storage = storage
        self.operation = operation
        self.columns = columns
        self.data = data
        self.on_conflict = on_conflict
        self.filters = []
        self.ordering = None
        self.limit_count = None
    
    def eq(self, column: str, value: Any):
        """Mock equality filter"""
        self.filters.append(("eq", column, value))
        return self
    
    def order(self, column: str, desc: bool = False):
        """Mock ordering"""
        self.ordering = (column, desc)
        return self
    
    def limit(self, count: int):
        """Mock limit"""
        self.limit_count = count
        return self
    
    def single(self):
        """Mock single result"""
        self.single_result = True
        return self
    
    def execute(self):
        """Execute the mock query"""
        try:
            if self.operation == "select":
                return self._execute_select()
            elif self.operation == "insert":
                return self._execute_insert()
            elif self.operation == "update": 
                return self._execute_update()
            elif self.operation == "delete":
                return self._execute_delete()
            elif self.operation == "upsert":
                return self._execute_upsert()
        except Exception as e:
            return MockSupabaseResponse(data=None, error=str(e))
    
    def _execute_select(self):
        """Execute select operation"""
        results = list(self.storage.values())
        
        # Apply filters
        for filter_type, column, value in self.filters:
            if filter_type == "eq":
                results = [r for r in results if r.get(column) == value]
        
        # Apply ordering
        if self.ordering:
            column, desc = self.ordering
            results.sort(key=lambda x: x.get(column, ""), reverse=desc)
        
        # Apply limit
        if self.limit_count:
            results = results[:self.limit_count]
        
        # Handle single result
        if hasattr(self, 'single_result'):
            return MockSupabaseResponse(data=results[0] if results else None)
        
        return MockSupabaseResponse(data=results)
    
    def _execute_insert(self):
        """Execute insert operation"""
        record_id = generate_id()
        new_record = {**self.data, "id": record_id, "created_at": get_current_timestamp()}
        self.storage[record_id] = new_record
        return MockSupabaseResponse(data=[new_record])
    
    def _execute_update(self):
        """Execute update operation"""
        updated_records = []
        for filter_type, column, value in self.filters:
            if filter_type == "eq":
                for record_id, record in self.storage.items():
                    if record.get(column) == value:
                        record.update(self.data)
                        record["updated_at"] = get_current_timestamp()
                        updated_records.append(record)
        return MockSupabaseResponse(data=updated_records)
    
    def _execute_delete(self):
        """Execute delete operation"""
        deleted_records = []
        to_delete = []
        for filter_type, column, value in self.filters:
            if filter_type == "eq":
                for record_id, record in self.storage.items():
                    if record.get(column) == value:
                        deleted_records.append(record)
                        to_delete.append(record_id)
        
        for record_id in to_delete:
            del self.storage[record_id]
        
        return MockSupabaseResponse(data=deleted_records)
    
    def _execute_upsert(self):
        """Execute upsert operation"""
        # For mock implementation, treat as insert for simplicity
        # In real implementation, this would check for conflicts
        if self.on_conflict and "user_id" in self.on_conflict:
            # Check if record exists with same user_id
            user_id = self.data.get("user_id")
            existing_record = None
            for record_id, record in self.storage.items():
                if record.get("user_id") == user_id:
                    existing_record = record_id
                    break
            
            if existing_record:
                # Update existing
                self.storage[existing_record].update(self.data)
                self.storage[existing_record]["updated_at"] = get_current_timestamp()
                return MockSupabaseResponse(data=[self.storage[existing_record]])
        
        # Insert new
        return self._execute_insert()

class MockSupabaseClient:
    """Mock Supabase client that mimics the real client interface"""
    
    def table(self, table_name: str):
        """Get mock table interface"""
        return MockSupabaseTable(table_name)


# INITIALIZE ON IMPORT

# Auto-initialize when module is imported
initialize_mock_data()

# Export the mock client
mock_supabase = MockSupabaseClient()
