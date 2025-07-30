// src/components/inputs/InputField.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// No explicit import for jest-dom/extend-expect needed here if setupTests.ts works
// import '@testing-library/jest-dom/extend-expect'; // REMOVE THIS LINE IF IT'S CAUSING ISSUES AND RELY ON setupTests.ts

import InputField from './InputField';

describe('InputField', () => {
  test('renders with correct label and initial value', () => {
    render(
      <InputField
        name="testInput"
        label="Test Label"
        value="Initial Value"
        onChange={jest.fn()}
      />
    );

    expect(screen.getByLabelText(/Test Label/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue(/Initial Value/i)).toBeInTheDocument();
  });

  test('calls onChange handler when input value changes', async () => {
    const handleChange = jest.fn();
    render(
      <InputField
        name="testInput"
        label="Test Label"
        value=""
        onChange={handleChange}
      />
    );

    const input = screen.getByLabelText(/Test Label/i);
    await userEvent.type(input, 'hello');

    expect(handleChange).toHaveBeenCalledTimes(5);
    expect(handleChange).toHaveBeenLastCalledWith(
      expect.objectContaining({
        target: expect.objectContaining({
          name: 'testInput',
          value: 'hello',
        }),
      })
    );
  });

  // Test Case 3: Displays error message and styling when error prop is true
  test('displays error message and styling when error prop is true', () => {
    render(
      <InputField
        name="testInput"
        label="Test Label"
        value=""
        onChange={jest.fn()}
        error={true}
        helperText="This is an error message."
      />
    );

    const input = screen.getByLabelText(/Test Label/i);
    // --- FIX FOR toHaveAriaInvalid: Use toHaveAttribute directly ---
    expect(input).toHaveAttribute('aria-invalid', 'true');
    // --- End Fix ---
    
    // Material-UI often applies the 'Mui-error' class to the input's parent wrapper
    expect(input.parentElement).toHaveClass('Mui-error'); // This should work if jest-dom loads

    expect(screen.getByText(/This is an error message./i)).toBeInTheDocument();
  });

  test('renders as required when required prop is true', () => {
    render(
      <InputField
        name="testInput"
        label="Test Label"
        value=""
        onChange={jest.fn()}
        required={true}
      />
    );

    const input = screen.getByLabelText(/Test Label/i);
    expect(input).toHaveAttribute('required');
  });

  test('renders as disabled when disabled prop is true', () => {
    render(
      <InputField
        name="testInput"
        label="Test Label"
        value="Disabled Value"
        onChange={jest.fn()}
        disabled={true}
      />
    );

    const input = screen.getByLabelText(/Test Label/i);
    expect(input).toBeDisabled();
  });

  test('renders with specific type', () => {
    render(
      <InputField
        name="passwordInput"
        label="Password"
        value=""
        onChange={jest.fn()}
        type="password"
      />
    );

    const input = screen.getByLabelText(/Password/i);
    expect(input).toHaveAttribute('type', 'password');
  });

  test('renders with placeholder text', () => {
    render(
      <InputField
        name="searchInput"
        label="Search"
        value=""
        onChange={jest.fn()}
        placeholder="Enter search term"
      />
    );

    expect(screen.getByPlaceholderText(/Enter search term/i)).toBeInTheDocument();
  });

  test('renders as multiline (textarea) with specified rows', () => {
    render(
      <InputField
        name="description"
        label="Description"
        value=""
        onChange={jest.fn()}
        multiline={true}
        rows={4}
      />
    );

    const textarea = screen.getByLabelText(/Description/i);
    expect(textarea.tagName).toBe('TEXTAREA');
    expect(textarea).toHaveAttribute('rows', '4');
  });

  test('InputLabel shrinks for type="date" even if empty', () => {
    render(
      <InputField
        name="dateInput"
        label="Date"
        value=""
        onChange={jest.fn()}
        type="date"
      />
    );

    const labelElement = screen.getByLabelText(/Date/i).closest('div')?.querySelector('label');
    expect(labelElement).toHaveClass('MuiInputLabel-shrink');
  });

  test('InputLabel shrinks if value is present for text input', () => {
    render(
      <InputField
        name="nameInput"
        label="Name"
        value="Some text"
        onChange={jest.fn()}
        type="text"
      />
    );
    const labelElement = screen.getByLabelText(/Name/i).closest('div')?.querySelector('label');
    expect(labelElement).toHaveClass('MuiInputLabel-shrink');
  });
});