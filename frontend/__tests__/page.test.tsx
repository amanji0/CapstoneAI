import { render, screen, fireEvent } from '@testing-library/react'
import Page from '../src/app/page'

describe('CapstoneAI Application', () => {
  it('renders the landing page correctly', () => {
    render(<Page />)
    
    // Check if main heading is present (will find multiple instances due to Navbar)
    const headings = screen.getAllByText(/Capstone/i)
    expect(headings.length).toBeGreaterThan(0)
    
    // Check if the get started button is present
    const getStartedButton = screen.getByRole('button', { name: /Start generating project ideas/i })
    expect(getStartedButton).toBeInTheDocument()
  })

  it('navigates to the form step and checks inputs', () => {
    render(<Page />)
    
    const getStartedButton = screen.getByRole('button', { name: /Start generating project ideas/i })
    fireEvent.click(getStartedButton)
    
    // Should now show the form
    expect(screen.getByText(/Tell us about yourself/i)).toBeInTheDocument()
    
    // Check form fields
    const nameInput = screen.getByLabelText(/Your Name/i)
    expect(nameInput).toBeInTheDocument()
    
    const fieldSelect = screen.getByLabelText(/Academic Field/i)
    expect(fieldSelect).toBeInTheDocument()

    // Test form interaction
    fireEvent.change(nameInput, { target: { value: 'Test User' } })
    expect(nameInput).toHaveValue('Test User')
    
    // Check GitHub input is present
    expect(screen.getByLabelText(/GitHub Profile URL/i)).toBeInTheDocument()
  })
})
