"""
Example Selenium test with broken XPath selectors
This represents a typical scenario where DOM structure changes broke the tests
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestLoginPage:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
    
    def teardown_method(self):
        self.driver.quit()
    
    def test_successful_login(self):
        """Test that a user can login with valid credentials"""
        self.driver.get("https://example.com/login")
        
        # BROKEN: These absolute XPaths break when DOM structure changes
        username_field = self.driver.find_element(
            By.XPATH, 
            "/html/body/div[1]/div[2]/div[1]/form/div[1]/input"
        )
        password_field = self.driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/form/div[2]/input"
        )
        submit_button = self.driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/form/div[3]/button"
        )
        
        # Enter credentials
        username_field.send_keys("testuser@example.com")
        password_field.send_keys("SecurePassword123!")
        submit_button.click()
        
        # BROKEN: Brittle selector for success message
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, 
                "/html/body/div[1]/div[1]/div[1]/span"
            ))
        )
        
        assert "Welcome" in success_message.text
    
    def test_login_validation(self):
        """Test that validation errors appear for invalid input"""
        self.driver.get("https://example.com/login")
        
        # BROKEN: Index-based selector
        submit_button = self.driver.find_element(
            By.XPATH,
            "//button[1]"
        )
        
        # Click submit without entering credentials
        submit_button.click()
        
        # BROKEN: Brittle error message selector
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "/html/body/div[1]/div[2]/div[1]/form/div[4]/span"
            ))
        )
        
        assert "required" in error_message.text.lower()
    
    def test_forgot_password_link(self):
        """Test that forgot password link navigates correctly"""
        self.driver.get("https://example.com/login")
        
        # BROKEN: Position-based selector that's too specific
        forgot_password_link = self.driver.find_element(
            By.XPATH,
            "//div[@class='form-container']/form/div[5]/a[1]"
        )
        
        forgot_password_link.click()
        
        # Wait for navigation
        time.sleep(2)
        
        assert "/forgot-password" in self.driver.current_url
    
    def test_remember_me_checkbox(self):
        """Test that remember me checkbox can be toggled"""
        self.driver.get("https://example.com/login")
        
        # BROKEN: Very brittle selector
        checkbox = self.driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[1]/form/div[3]/label/input"
        )
        
        # Toggle checkbox
        checkbox.click()
        assert checkbox.is_selected()
        
        checkbox.click()
        assert not checkbox.is_selected()
    
    def test_social_login_buttons(self):
        """Test that social login buttons are present"""
        self.driver.get("https://example.com/login")
        
        # BROKEN: These will break if order changes
        google_button = self.driver.find_element(
            By.XPATH,
            "//div[@class='social-login']/button[1]"
        )
        facebook_button = self.driver.find_element(
            By.XPATH,
            "//div[@class='social-login']/button[2]"
        )
        
        assert google_button.is_displayed()
        assert facebook_button.is_displayed()