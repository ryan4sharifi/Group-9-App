import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.routes import report
from app.routes.report import ReportFilter, VolunteerReport, EventReport
from app.routes.auth import create_access_token
from datetime import datetime, timedelta

app = FastAPI()
app.include_router(report.router)

# Test data
valid_report_filter = {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "event_id": "event123",
    "user_id": "user123",
    "status": "Attended"
}

# Test: Volunteer Participation Report
@patch("app.routes.report.supabase")
def test_volunteer_participation_report_success(mock_supabase):
    """Test successful volunteer participation report generation"""
    # Mock volunteer history data
    history_data = [
        {
            "user_id": "user123",
            "status": "Attended",
            "user_profiles": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "skills": ["teamwork", "communication"]
            },
            "events": {
                "name": "Beach Cleanup",
                "event_date": "2024-01-15"
            }
        },
        {
            "user_id": "user123",
            "status": "Signed Up",
            "user_profiles": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "skills": ["teamwork", "communication"]
            },
            "events": {
                "name": "Food Drive",
                "event_date": "2024-01-20"
            }
        }
    ]
    
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = history_data
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/volunteers", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert len(data["reports"]) == 1
    assert data["reports"][0]["full_name"] == "John Doe"
    assert data["reports"][0]["total_events"] == 2
    assert data["reports"][0]["completed_events"] == 1
    assert data["reports"][0]["attendance_rate"] == 50.0

@patch("app.routes.report.supabase")
def test_volunteer_participation_report_unauthorized(mock_supabase):
    """Test volunteer participation report without admin access"""
    # Create non-admin token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/volunteers", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

@patch("app.routes.report.supabase")
def test_volunteer_participation_report_with_filters(mock_supabase):
    """Test volunteer participation report with filters"""
    # Mock filtered data
    history_data = [
        {
            "user_id": "user123",
            "status": "Attended",
            "user_profiles": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "skills": ["teamwork"]
            },
            "events": {
                "name": "Beach Cleanup",
                "event_date": "2024-01-15"
            }
        }
    ]
    
    mock_supabase.table.return_value.select.return_value.gte.return_value.lte.return_value.eq.return_value.eq.return_value.execute.return_value.data = history_data
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/volunteers", params=valid_report_filter, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["reports"]) == 1

@patch("app.routes.report.supabase")
def test_volunteer_participation_report_server_error(mock_supabase):
    """Test volunteer participation report with server error"""
    # Mock server error
    mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception("Database error")
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/volunteers", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Test: Event Participation Summary
@patch("app.routes.report.supabase")
def test_event_participation_summary_success(mock_supabase):
    """Test successful event participation summary generation"""
    # Mock events data
    events_data = [
        {
            "id": "event123",
            "name": "Beach Cleanup",
            "event_date": "2024-01-15",
            "location": "Miami Beach",
            "required_skills": ["teamwork"],
            "urgency": "high"
        }
    ]
    
    # Mock history data
    history_data = [
        {
            "event_id": "event123",
            "status": "Attended"
        },
        {
            "event_id": "event123",
            "status": "Signed Up"
        }
    ]
    
    # Mock events query
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = events_data
    
    # Mock history query
    mock_supabase.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = history_data
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/events", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert "event_reports" in data
    assert len(data["event_reports"]) == 1
    assert data["event_reports"][0]["event_name"] == "Beach Cleanup"
    assert data["event_reports"][0]["total_volunteers"] == 2
    assert data["event_reports"][0]["attended_volunteers"] == 1
    assert data["event_reports"][0]["completion_rate"] == 50.0

@patch("app.routes.report.supabase")
def test_event_participation_summary_unauthorized(mock_supabase):
    """Test event participation summary without admin access"""
    # Create non-admin token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/events", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

@patch("app.routes.report.supabase")
def test_event_participation_summary_no_events(mock_supabase):
    """Test event participation summary with no events"""
    # Mock empty events data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/events", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["event_reports"] == []

# Test: Analytics Dashboard
@patch("app.routes.report.supabase")
def test_analytics_dashboard_success(mock_supabase):
    """Test successful analytics dashboard generation"""
    # Mock summary data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"user_id": "user1"},
        {"user_id": "user2"}
    ]
    
    # Mock events data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"id": "event1"},
        {"id": "event2"}
    ]
    
    # Mock history data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"id": "history1"},
        {"id": "history2"},
        {"id": "history3"}
    ]
    
    # Mock recent activity
    mock_supabase.table.return_value.select.return_value.gte.return_value.execute.return_value.data = [
        {
            "created_at": "2024-01-15T10:00:00",
            "status": "Attended"
        },
        {
            "created_at": "2024-01-20T10:00:00",
            "status": "Signed Up"
        }
    ]
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/analytics", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "engagement_by_month" in data
    assert "generated_at" in data
    assert data["summary"]["total_volunteers"] == 2
    assert data["summary"]["total_events"] == 2
    assert data["summary"]["total_participations"] == 3

@patch("app.routes.report.supabase")
def test_analytics_dashboard_unauthorized(mock_supabase):
    """Test analytics dashboard without admin access"""
    # Create non-admin token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/analytics", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

# Test: Pydantic Models
def test_report_filter_model():
    """Test ReportFilter model validation"""
    filter_data = ReportFilter(
        start_date="2024-01-01",
        end_date="2024-12-31",
        event_id="event123",
        user_id="user123",
        status="Attended"
    )
    
    assert filter_data.start_date == "2024-01-01"
    assert filter_data.end_date == "2024-12-31"
    assert filter_data.event_id == "event123"
    assert filter_data.user_id == "user123"
    assert filter_data.status == "Attended"

def test_report_filter_model_defaults():
    """Test ReportFilter model with default values"""
    filter_data = ReportFilter()
    
    assert filter_data.start_date is None
    assert filter_data.end_date is None
    assert filter_data.event_id is None
    assert filter_data.user_id is None
    assert filter_data.status is None

def test_volunteer_report_model():
    """Test VolunteerReport model validation"""
    report_data = VolunteerReport(
        user_id="user123",
        full_name="John Doe",
        email="john@example.com",
        total_events=5,
        completed_events=4,
        attendance_rate=80.0,
        skills=["teamwork", "communication"],
        recent_activity=[
            {
                "event_name": "Beach Cleanup",
                "date": "2024-01-15",
                "status": "Attended"
            }
        ]
    )
    
    assert report_data.user_id == "user123"
    assert report_data.full_name == "John Doe"
    assert report_data.email == "john@example.com"
    assert report_data.total_events == 5
    assert report_data.completed_events == 4
    assert report_data.attendance_rate == 80.0
    assert len(report_data.skills) == 2
    assert len(report_data.recent_activity) == 1

def test_event_report_model():
    """Test EventReport model validation"""
    report_data = EventReport(
        event_id="event123",
        event_name="Beach Cleanup",
        event_date="2024-01-15",
        location="Miami Beach",
        required_skills=["teamwork"],
        urgency="high",
        total_volunteers=10,
        attended_volunteers=8,
        completion_rate=80.0
    )
    
    assert report_data.event_id == "event123"
    assert report_data.event_name == "Beach Cleanup"
    assert report_data.event_date == "2024-01-15"
    assert report_data.location == "Miami Beach"
    assert len(report_data.required_skills) == 1
    assert report_data.urgency == "high"
    assert report_data.total_volunteers == 10
    assert report_data.attended_volunteers == 8
    assert report_data.completion_rate == 80.0

# Test: Edge Cases
@patch("app.routes.report.supabase")
def test_volunteer_participation_report_zero_events(mock_supabase):
    """Test volunteer participation report with zero events"""
    # Mock empty history data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/volunteers", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["reports"] == []

@patch("app.routes.report.supabase")
def test_volunteer_participation_report_missing_profile(mock_supabase):
    """Test volunteer participation report with missing profile data"""
    # Mock history data with missing profile
    history_data = [
        {
            "user_id": "user123",
            "status": "Attended",
            "user_profiles": None,
            "events": {
                "name": "Beach Cleanup",
                "event_date": "2024-01-15"
            }
        }
    ]
    
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = history_data
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/volunteers", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["reports"]) == 1
    assert data["reports"][0]["full_name"] == "Unknown"

@patch("app.routes.report.supabase")
def test_event_participation_summary_zero_volunteers(mock_supabase):
    """Test event participation summary with zero volunteers"""
    # Mock events data
    events_data = [
        {
            "id": "event123",
            "name": "Beach Cleanup",
            "event_date": "2024-01-15",
            "location": "Miami Beach",
            "required_skills": ["teamwork"],
            "urgency": "high"
        }
    ]
    
    # Mock empty history data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = events_data
    mock_supabase.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = []
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/events", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["event_reports"]) == 1
    assert data["event_reports"][0]["total_volunteers"] == 0
    assert data["event_reports"][0]["completion_rate"] == 0.0

# Test: Error Handling
@patch("app.routes.report.supabase")
def test_volunteer_participation_report_database_error(mock_supabase):
    """Test volunteer participation report with database error"""
    # Mock database error
    mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception("Connection failed")
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/volunteers", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 500
    assert "Connection failed" in response.json()["detail"]

@patch("app.routes.report.supabase")
def test_event_participation_summary_database_error(mock_supabase):
    """Test event participation summary with database error"""
    # Mock database error
    mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception("Query failed")
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/reports/events", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 500
    assert "Query failed" in response.json()["detail"]

# Test: Integration Scenarios
@patch("app.routes.report.supabase")
def test_complete_reporting_workflow(mock_supabase):
    """Test complete reporting workflow"""
    # Mock data for all reports
    history_data = [
        {
            "user_id": "user123",
            "status": "Attended",
            "user_profiles": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "skills": ["teamwork"]
            },
            "events": {
                "name": "Beach Cleanup",
                "event_date": "2024-01-15"
            }
        }
    ]
    
    events_data = [
        {
            "id": "event123",
            "name": "Beach Cleanup",
            "event_date": "2024-01-15",
            "location": "Miami Beach",
            "required_skills": ["teamwork"],
            "urgency": "high"
        }
    ]
    
    # Mock all queries
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = history_data
    mock_supabase.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = history_data
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    
    # Test volunteer report
    response = client.get("/reports/volunteers", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Test event report
    response = client.get("/reports/events", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Test analytics dashboard
    response = client.get("/reports/analytics", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200 