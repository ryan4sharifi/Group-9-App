// src/App.test.tsx

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter as Router } from 'react-router-dom'; // Using BrowserRouter for full app simulation
import App from './App'; // The main App component
import { UserProvider } from './context/UserContext'; // Your UserProvider
import axios from 'axios'; // <--- ADDED: Explicit import for axios

// Mock axios to prevent actual API calls during tests
// This is crucial because pages like ProfilePage, MatchPage, etc., make API calls on mount.
jest.mock('axios', () => ({
  ...jest.requireActual('axios'), // Keep actual axios methods like create, defaults, etc.
  get: jest.fn(), // Mock .get method for data fetching
  post: jest.fn(), // Mock .post method for login/register/profile updates
  put: jest.fn(), // Mock .put method for updates
  delete: jest.fn(), // Mock .delete method for deletion
}));

// Mock sessionStorage as it's used by UserContext for persistence
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


describe('App Component (Integration Tests)', () => {
  // Clear mocks and sessionStorage before each test to ensure test isolation
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
  });

  // Test Case One: Renders HomePage by default when not logged in
  test('renders HomePage by default when not logged in', async () => {
    sessionStorage.clear(); // Ensure no user in session

    render(
      <Router>
        <UserProvider>
          <App />
        </UserProvider>
      </Router>
    );

    // Expect to see content from HomePage
    // Adjust this text based on your actual HomePage content
    await waitFor(() => {
      expect(screen.getByText(/Welcome to the Volunteer Portal/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Login/i })).toBeInTheDocument(); // Login link should be visible in Navbar
    });
  });

  // Test Case 2: Protected routes redirect to Login page when not logged in
  test('protected routes redirect to Login page when not logged in', async () => {
    sessionStorage.clear(); // Ensure no user in session

    render(
      <Router>
        <UserProvider>
          <App />
        </UserProvider>
      </Router>
    );

    // Simulate clicking a link to a protected route (e.g., Profile)
    // If your Navbar hides protected links when not logged in, this test would need to simulate
    // direct navigation, e.g., using history.push() from react-router-dom/test.
    // For this test, assuming the 'Profile' link is rendered in the Navbar even for logged-out users,
    // and clicking it triggers the redirect.
    const profileLink = screen.queryByRole('link', { name: /Profile/i });
    if (profileLink) {
      userEvent.click(profileLink);
    } else {
      // Fallback if link is not rendered for logged-out users:
      // This part would involve configuring a MemoryRouter with an initialEntries and then asserting the redirect.
      // For simplicity in a BrowserRouter context, ensure Navbar renders the link for all, or skip this specific click.
    }

    // Wait for the Login page content to appear after redirect
    await waitFor(() => {
      expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument(); // Text from LoginPage
      expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument(); // Button from LoginPage
    }, { timeout: 3000 }); // Increase timeout if needed
  });


  // Test Case 3: Renders protected routes correctly when logged in
  test('renders protected routes correctly when logged in', async () => {
    // Simulate being logged in for this test
    sessionStorage.setItem('user_id', 'mock-user-id');
    sessionStorage.setItem('role', 'volunteer');

    // Mock API calls that ProfilePage makes on mount
    (axios.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/api/profile/')) {
        return Promise.resolve({ data: { full_name: 'Test Volunteer', skills: ['react'], created_at: new Date().toISOString() } }); // Added created_at for lastUpdated
      }
      if (url.includes('/auth/user/')) {
        return Promise.resolve({ data: { email: 'test@example.com', role: 'volunteer' } });
      }
      return Promise.reject(new Error(`Not mocked GET: ${url}`));
    });

    render(
      <Router>
        <UserProvider>
          <App />
        </UserProvider>
      </Router>
    );

    // Click the Profile link in the Navbar (assuming it's visible when logged in)
    const profileLink = screen.getByRole('link', { name: /Profile/i });
    userEvent.click(profileLink);

    // Wait for the Profile page content to appear
    await waitFor(() => {
      expect(screen.getByText(/Your Profile/i)).toBeInTheDocument();
      expect(screen.getByText(/Test Volunteer/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Save Profile/i })).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  // Test Case 4: Admin user sees Reports link and can navigate
  test('admin user sees Reports link and can navigate', async () => {
    sessionStorage.setItem('user_id', 'mock-admin-id');
    sessionStorage.setItem('role', 'admin');

    // Mock API calls ReportPage makes on mount (if any, e.g., initial report fetch)
    (axios.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/api/profile/')) { // ProfilePage might fetch profile
        return Promise.resolve({ data: { full_name: 'Test Admin', skills: [], created_at: new Date().toISOString() } });
      }
      if (url.includes('/auth/user/')) { // ProfilePage might fetch credentials
        return Promise.resolve({ data: { email: 'admin@example.com', role: 'admin' } });
      }
      if (url.includes('/api/reports/volunteers')) { // ReportPage fetches reports
        return Promise.resolve({ data: { report: [] } });
      }
      if (url.includes('/api/reports/events')) { // ReportPage fetches reports
        return Promise.resolve({ data: { event_summary: [] } });
      }
      return Promise.reject(new Error(`Not mocked GET: ${url}`));
    });

    render(
      <Router>
        <UserProvider>
          <App />
        </UserProvider>
      </Router>
    );

    // Assert that the Reports link is visible in the Navbar
    const reportsLink = screen.getByRole('link', { name: /Reports/i });
    expect(reportsLink).toBeInTheDocument();

    // Click the Reports link
    userEvent.click(reportsLink);

    // Wait for the ReportPage content to appear
    await waitFor(() => {
      expect(screen.getByText(/Reporting Module/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Volunteer Participation Report/i })).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  // Test Case 5: Non-admin user does NOT see Reports link
  test('non-admin user does NOT see Reports link', async () => {
    sessionStorage.setItem('user_id', 'mock-volunteer-id');
    sessionStorage.setItem('role', 'volunteer');

    // Mock API calls that might happen on initial render (e.g., ProfilePage if navigated there)
    (axios.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/api/profile/')) {
        return Promise.resolve({ data: { full_name: 'Test Volunteer', skills: ['react'], created_at: new Date().toISOString() } });
      }
      if (url.includes('/auth/user/')) {
        return Promise.resolve({ data: { email: 'volunteer@example.com', role: 'volunteer' } });
      }
      return Promise.reject(new Error(`Not mocked GET: ${url}`));
    });

    render(
      <Router>
        <UserProvider>
          <App />
        </UserProvider>
      </Router>
    );

    // Assert that the Reports link is NOT visible in the Navbar
    expect(screen.queryByRole('link', { name: /Reports/i })).not.toBeInTheDocument();
    // You might also assert that other common links *are* visible, e.g., 'Events' link
    expect(screen.getByRole('link', { name: /Events/i })).toBeInTheDocument();
  });

  // logout test case
  test('logout clears session and redirects to home', async () => {
  sessionStorage.setItem('user_id', 'mock-user-id');
  sessionStorage.setItem('role', 'volunteer');

  render(
    <Router>
      <UserProvider>
        <App />
      </UserProvider>
    </Router>
  );

  const logoutButton = screen.getByRole('button', { name: /Logout/i });
  userEvent.click(logoutButton);

  await waitFor(() => {
    expect(screen.getByText(/Welcome to the Volunteer Portal/i)).toBeInTheDocument();
    expect(sessionStorage.getItem('user_id')).toBeNull(); // confirm it's cleared
  });
});

});

// Navbar hides protected links after logout
test('navbar hides protected links after logout', async () => {
  sessionStorage.setItem('user_id', 'vol-id');
  sessionStorage.setItem('role', 'volunteer');

  render(
    <Router>
      <UserProvider>
        <App />
      </UserProvider>
    </Router>
  );

  const logoutButton = screen.getByRole('button', { name: /Logout/i });
  userEvent.click(logoutButton);

  await waitFor(() => {
    expect(screen.queryByRole('link', { name: /Profile/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Events/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Match/i })).not.toBeInTheDocument();
  });
});

// shows loading state during async operations
test('shows loading indicator when fetching data', async () => {
  sessionStorage.setItem('user_id', 'user123');
  sessionStorage.setItem('role', 'volunteer');

  (axios.get as jest.Mock).mockImplementation(() => {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ data: {} });
      }, 1000); // simulate delay
    });
  });

  render(
    <Router>
      <UserProvider>
        <App />
      </UserProvider>
    </Router>
  );

  // Expect some kind of loading text/spinner early
  expect(screen.getByText(/Loading/i)).toBeInTheDocument(); // change text if needed
});
