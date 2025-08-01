// src/pages/LoginPage.test.tsx

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react'; // Added fireEvent for change events
import userEvent from '@testing-library/user-event';
import { BrowserRouter as Router } from 'react-router-dom';
import LoginPage from './LoginPage';
import { UserProvider } from '../context/UserContext';
import axios from 'axios';

// Mock axios methods used in LoginPage
jest.mock('axios', () => ({
  ...jest.requireActual('axios'),
  post: jest.fn(), // Mock axios.post
}));

// Mock sessionStorage as it's used in UserContext for persistence
const sessionStorageMock = (() => {
  let store: { [key: string]: string } = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString(); },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock });


describe('LoginPage', () => {
  // Clear mocks and sessionStorage before each test to ensure test isolation
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
  });

  // Test Case 1: Renders all expected login form elements
  test('renders all login form elements', () => {
    render(
      <Router>
        <UserProvider>
          <LoginPage />
        </UserProvider>
      </Router>
    );

    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument(); // Changed from 'Login' to 'Sign In'
    expect(screen.getByText(/Don't have an account?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Sign up/i })).toBeInTheDocument(); // Check for the Sign up link
  });

  // Test Case 2: Shows client-side validation errors for empty fields on submit
  test('shows client-side validation errors for empty fields on submit', async () => {
    render(
      <Router>
        <UserProvider>
          <LoginPage />
        </UserProvider>
      </Router>
    );

    userEvent.click(screen.getByRole('button', { name: /Sign In/i }));

    // Wait for the asynchronous validation messages to appear
    await screen.findByText(/Email is required./i);
    expect(screen.getByText(/Password is required./i)).toBeInTheDocument();
    expect(screen.getByText(/Please fill in all required fields./i)).toBeInTheDocument(); // General API error for client-side validation

    // Ensure axios.post was NOT called as client-side validation failed
    expect(axios.post).not.toHaveBeenCalled();
  });

  // Test Case 3: Shows client-side validation error for invalid email format
  test('shows client-side validation error for invalid email format', async () => {
    render(
      <Router>
        <UserProvider>
          <LoginPage />
        </UserProvider>
      </Router>
    );

    userEvent.type(screen.getByLabelText(/Email Address/i), 'invalid-email');
    userEvent.type(screen.getByLabelText(/Password/i), 'password123'); // Fill password to ensure only email error is shown

    userEvent.click(screen.getByRole('button', { name: /Sign In/i }));

    await screen.findByText(/Invalid email format./i);
    expect(axios.post).not.toHaveBeenCalled();
  });

  // Test Case 4: Clears errors when input values change after an error
  test('clears errors when input values change after an error', async () => {
    render(
      <Router>
        <UserProvider>
          <LoginPage />
        </UserProvider>
      </Router>
    );

    userEvent.click(screen.getByRole('button', { name: /Sign In/i })); // Trigger errors
    await screen.findByText(/Email is required./i);

    userEvent.type(screen.getByLabelText(/Email Address/i), 'test@example.com'); // Type in email field
    expect(screen.queryByText(/Email is required./i)).not.toBeInTheDocument(); // Email error should disappear
    expect(screen.queryByText(/Please fill in all required fields./i)).not.toBeInTheDocument(); // General error should disappear

    userEvent.type(screen.getByLabelText(/Password/i), 'password123'); // Type in password field
    expect(screen.queryByText(/Password is required./i)).not.toBeInTheDocument(); // Password error should disappear
  });

  // Test Case 5: Submits form with valid data and navigates on success
  test('submits form with valid data and navigates on success', async () => {
    // Mock a successful login response from the backend
    (axios.post as jest.Mock).mockResolvedValueOnce({
      data: {
        message: 'Login successful',
        user_id: 'test-user-id',
        role: 'volunteer'
      }
    });

    render(
      <Router>
        <UserProvider>
          <LoginPage />
        </UserProvider>
      </Router>
    );

    userEvent.type(screen.getByLabelText(/Email Address/i), 'test@example.com');
    userEvent.type(screen.getByLabelText(/Password/i), 'password123');
    userEvent.click(screen.getByRole('button', { name: /Sign In/i }));

    await waitFor(() => {
      // Assert axios.post was called correctly
      expect(axios.post).toHaveBeenCalledTimes(1);
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/auth/login',
        { email: 'test@example.com', password: 'password123' }
      );

      // Assert sessionStorage items are set correctly
      expect(sessionStorage.getItem('user_id')).toBe('test-user-id');
      expect(sessionStorage.getItem('role')).toBe('volunteer');

      // Assert navigation happened (by checking for elements on the /profile page)
      // This relies on your App.tsx setup to render the ProfilePage after successful login
      expect(screen.getByText(/Your Profile/i)).toBeInTheDocument(); // Text from ProfilePage
      expect(screen.getByRole('button', { name: /Save Profile/i })).toBeInTheDocument(); // Button from ProfilePage
    }, { timeout: 3000 }); // Increased timeout for navigation
  });

  // Test Case 6: Shows general API error message on failed login (e.g., Invalid credentials from backend)
  test('shows general API error message on failed login', async () => {
  // Make axios.post fail with "Invalid credentials" error
  (axios.post as jest.Mock).mockRejectedValueOnce({
    response: {
      data: { detail: 'Invalid credentials.' },
      status: 401,
    },
  });

  // Show the login page
  render(
    <Router>
      <UserProvider>
        <LoginPage />
      </UserProvider>
    </Router>
  );

  // Enter wrong email and password
  userEvent.type(screen.getByLabelText(/Email Address/i), 'wrong@example.com');
  userEvent.type(screen.getByLabelText(/Password/i), 'wrongpassword');

  // Click the "Sign In" button
  userEvent.click(screen.getByRole('button', { name: /Sign In/i }));

  // Wait until the error message appears
  await waitFor(() => {
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent(/Invalid credentials./i);
  });

  // Check session storage does NOT have user_id after failed login
  expect(sessionStorage.getItem('user_id')).toBeNull();
});


  // Test Case 7: Navigates to register page when "Sign up" link is clicked
  test('navigates to register page when "Sign up" link is clicked', async () => {
    render(
      <Router>
        <UserProvider>
          <LoginPage />
        </UserProvider>
      </Router>
    );

    const signUpLink = screen.getByRole('link', { name: /Sign up/i });
    userEvent.click(signUpLink);

    // After clicking the link, verify that elements from the RegisterPage are present.
    // This requires that the RegisterPage route is correctly configured in App.tsx
    // and that its content is rendered after navigation.
    await screen.findByText(/Create Account/i); // Check for text on RegisterPage
    expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument(); // Check for an element specific to RegisterPage
  });
});