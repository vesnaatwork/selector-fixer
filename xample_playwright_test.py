"""
Example Playwright test with working selectors
This represents the same test scenarios but with robust, working selectors
"""

from playwright.sync_api import Page, expect
import pytest


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


def test_successful_login(page: Page):
    """Test that a user can login with valid credentials"""
    page.goto("https://example.com/login")
    
    # WORKING: Using stable ID selectors
    page.locator('#username').fill('testuser@example.com')
    page.locator('#password').fill('SecurePassword123!')
    page.locator('button[type="submit"]').click()
    
    # WORKING: Using data-testid attribute
    success_message = page.locator('[data-testid="success-message"]')
    expect(success_message).to_contain_text('Welcome')


def test_login_validation(page: Page):
    """Test that validation errors appear for invalid input"""
    page.goto("https://example.com/login")
    
    # WORKING: Using specific button type selector
    page.locator('button[type="submit"]').click()
    
    # WORKING: Using class selector for error message
    error_message = page.locator('.error-message')
    expect(error_message).to_contain_text('required', ignore_case=True)


def test_forgot_password_link(page: Page):
    """Test that forgot password link navigates correctly"""
    page.goto("https://example.com/login")
    
    # WORKING: Using text-based selector
    page.get_by_role('link', name='Forgot password?').click()
    
    # Verify navigation
    expect(page).to_have_url(/.*forgot-password/)


def test_remember_me_checkbox(page: Page):
    """Test that remember me checkbox can be toggled"""
    page.goto("https://example.com/login")
    
    # WORKING: Using name attribute
    checkbox = page.locator('input[name="remember"]')
    
    # Toggle checkbox
    checkbox.check()
    expect(checkbox).to_be_checked()
    
    checkbox.uncheck()
    expect(checkbox).not_to_be_checked()


def test_social_login_buttons(page: Page):
    """Test that social login buttons are present"""
    page.goto("https://example.com/login")
    
    # WORKING: Using data attributes for social login buttons
    google_button = page.locator('[data-provider="google"]')
    facebook_button = page.locator('[data-provider="facebook"]')
    
    expect(google_button).to_be_visible()
    expect(facebook_button).to_be_visible()