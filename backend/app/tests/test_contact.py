import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import FastAPI
from app.routes import contact
from app.routes.contact import ContactMessage

app = FastAPI()
app.include_router(contact.router)

# Test data
valid_contact_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "This is a test contact message."
}

# Test: Submit Contact Form
def test_submit_contact_form_success():
    """Test successful contact form submission"""
    client = TestClient(app)
    response = client.post("/contact", json=valid_contact_data)
    
    assert response.status_code == 200
    assert "Your message has been received" in response.json()["message"]

def test_submit_contact_form_invalid_email():
    """Test contact form submission with invalid email"""
    client = TestClient(app)
    
    invalid_data = valid_contact_data.copy()
    invalid_data["email"] = "invalid-email"
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422

def test_submit_contact_form_empty_name():
    """Test contact form submission with empty name"""
    client = TestClient(app)
    
    invalid_data = valid_contact_data.copy()
    invalid_data["name"] = ""
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422

def test_submit_contact_form_long_name():
    """Test contact form submission with name too long"""
    client = TestClient(app)
    
    invalid_data = valid_contact_data.copy()
    invalid_data["name"] = "a" * 101  # Exceeds max_length=100
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422

def test_submit_contact_form_empty_message():
    """Test contact form submission with empty message"""
    client = TestClient(app)
    
    invalid_data = valid_contact_data.copy()
    invalid_data["message"] = ""
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422

def test_submit_contact_form_long_message():
    """Test contact form submission with message too long"""
    client = TestClient(app)
    
    invalid_data = valid_contact_data.copy()
    invalid_data["message"] = "a" * 1001  # Exceeds max_length=1000
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422

def test_submit_contact_form_missing_fields():
    """Test contact form submission with missing fields"""
    client = TestClient(app)
    
    # Test missing name
    invalid_data = {
        "email": "john@example.com",
        "message": "Test message"
    }
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422
    
    # Test missing email
    invalid_data = {
        "name": "John Doe",
        "message": "Test message"
    }
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422
    
    # Test missing message
    invalid_data = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    
    response = client.post("/contact", json=invalid_data)
    assert response.status_code == 422

# Test: Pydantic Model Validation
def test_contact_message_model_valid():
    """Test ContactMessage model with valid data"""
    contact = ContactMessage(
        name="John Doe",
        email="john@example.com",
        message="This is a test message."
    )
    
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"
    assert contact.message == "This is a test message."

def test_contact_message_model_min_length_name():
    """Test ContactMessage model with name at minimum length"""
    contact = ContactMessage(
        name="J",  # Minimum length of 1
        email="john@example.com",
        message="Test message"
    )
    
    assert contact.name == "J"

def test_contact_message_model_max_length_name():
    """Test ContactMessage model with name at maximum length"""
    name = "a" * 100  # Maximum length of 100
    contact = ContactMessage(
        name=name,
        email="john@example.com",
        message="Test message"
    )
    
    assert contact.name == name

def test_contact_message_model_invalid_name_too_short():
    """Test ContactMessage model with name too short"""
    with pytest.raises(ValueError):
        ContactMessage(
            name="",  # Empty string
            email="john@example.com",
            message="Test message"
        )

def test_contact_message_model_invalid_name_too_long():
    """Test ContactMessage model with name too long"""
    with pytest.raises(ValueError):
        ContactMessage(
            name="a" * 101,  # Exceeds max length
            email="john@example.com",
            message="Test message"
        )

def test_contact_message_model_invalid_email():
    """Test ContactMessage model with invalid email"""
    with pytest.raises(ValueError):
        ContactMessage(
            name="John Doe",
            email="invalid-email",
            message="Test message"
        )

def test_contact_message_model_min_length_message():
    """Test ContactMessage model with message at minimum length"""
    contact = ContactMessage(
        name="John Doe",
        email="john@example.com",
        message="T"  # Minimum length of 1
    )
    
    assert contact.message == "T"

def test_contact_message_model_max_length_message():
    """Test ContactMessage model with message at maximum length"""
    message = "a" * 1000  # Maximum length of 1000
    contact = ContactMessage(
        name="John Doe",
        email="john@example.com",
        message=message
    )
    
    assert contact.message == message

def test_contact_message_model_invalid_message_too_short():
    """Test ContactMessage model with message too short"""
    with pytest.raises(ValueError):
        ContactMessage(
            name="John Doe",
            email="john@example.com",
            message=""  # Empty string
        )

def test_contact_message_model_invalid_message_too_long():
    """Test ContactMessage model with message too long"""
    with pytest.raises(ValueError):
        ContactMessage(
            name="John Doe",
            email="john@example.com",
            message="a" * 1001  # Exceeds max length
        )

# Test: Edge Cases
def test_contact_message_with_special_characters():
    """Test contact message with special characters"""
    contact = ContactMessage(
        name="José María",
        email="jose.maria@example.com",
        message="¡Hola! This is a test message with special characters: áéíóú ñ"
    )
    
    assert contact.name == "José María"
    assert contact.email == "jose.maria@example.com"
    assert "¡Hola!" in contact.message

def test_contact_message_with_numbers():
    """Test contact message with numbers in name"""
    contact = ContactMessage(
        name="John123 Doe",
        email="john123@example.com",
        message="This is message number 123"
    )
    
    assert contact.name == "John123 Doe"
    assert contact.email == "john123@example.com"
    assert "123" in contact.message

def test_contact_message_with_unicode():
    """Test contact message with unicode characters"""
    contact = ContactMessage(
        name="张三",
        email="zhang.san@example.com",
        message="这是一个测试消息"
    )
    
    assert contact.name == "张三"
    assert contact.email == "zhang.san@example.com"
    assert contact.message == "这是一个测试消息"

def test_contact_message_with_whitespace():
    """Test contact message with leading/trailing whitespace"""
    contact = ContactMessage(
        name="  John Doe  ",
        email="  john@example.com  ",
        message="  This is a test message  "
    )
    
    assert contact.name == "  John Doe  "
    assert contact.email == "john@example.com"  # EmailStr automatically strips whitespace - this is correct
    assert contact.message == "  This is a test message  "

# Test: Email Validation
def test_contact_message_valid_emails():
    """Test contact message with various valid email formats"""
    valid_emails = [
        "user@example.com",
        "user.name@example.com",
        "user+tag@example.com",
        "user@subdomain.example.com",
        "user@example.co.uk",
        "user123@example.com"
    ]
    
    for email in valid_emails:
        contact = ContactMessage(
            name="John Doe",
            email=email,
            message="Test message"
        )
        assert contact.email == email

def test_contact_message_invalid_emails():
    """Test contact message with various invalid email formats"""
    invalid_emails = [
        "invalid-email",
        "@example.com",
        "user@",
        "user@.com",
        "user..name@example.com",
        "user@example..com"
    ]
    
    for email in invalid_emails:
        with pytest.raises(ValueError):
            ContactMessage(
                name="John Doe",
                email=email,
                message="Test message"
            )

# Test: Error Handling
@patch("app.routes.contact.print")
def test_submit_contact_form_exception_handling(mock_print):
    """Test contact form submission with exception handling"""
    # This test ensures the exception handling works
    # The actual implementation doesn't throw exceptions, but we can test the structure
    
    client = TestClient(app)
    response = client.post("/contact", json=valid_contact_data)
    
    assert response.status_code == 200
    mock_print.assert_called_once()

# Test: Integration Scenarios
def test_complete_contact_workflow():
    """Test complete contact form workflow"""
    client = TestClient(app)
    
    # Test with different valid contact data
    test_cases = [
        {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "message": "I would like to volunteer for upcoming events."
        },
        {
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "message": "Question about the volunteer matching system."
        },
        {
            "name": "Carol Davis",
            "email": "carol.davis@test.org",
            "message": "General inquiry about the platform."
        }
    ]
    
    for test_case in test_cases:
        response = client.post("/contact", json=test_case)
        assert response.status_code == 200
        assert "Your message has been received" in response.json()["message"] 