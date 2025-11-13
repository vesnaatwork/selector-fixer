# Selenium Selector Fixer

Automatically fix broken Selenium XPath selectors using working Playwright tests and Claude AI.

## Overview

This tool uses Claude AI to intelligently map working Playwright selectors to broken Selenium XPaths and suggests improved, more robust selectors.

## Features

- 🤖 **AI-Powered Analysis**: Uses Claude to understand test intent and map selectors
- 🔄 **Automatic Updates**: Updates your Selenium test files with new selectors
- 📊 **Detailed Reports**: Generates comprehensive reports explaining each change
- 🛡️ **Robust Selectors**: Suggests selectors that are less likely to break
- 🎯 **Smart Mapping**: Matches Selenium and Playwright tests based on functionality

## Installation

### 1. Install Python Dependencies

```bash
pip install anthropic --break-system-packages
```

### 2. Set Up API Key

You need an Anthropic API key to use this tool. Get one at https://console.anthropic.com/

Set it as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or pass it directly via command line (see usage below).

### 3. Make the Script Executable

```bash
chmod +x selector_fixer.py
```

## Usage

### Basic Usage

```bash
python selector_fixer.py \
  --selenium tests/selenium_test.py \
  --playwright tests/playwright_test.py
```

### With Test Results

```bash
python selector_fixer.py \
  --selenium tests/selenium_test.py \
  --playwright tests/playwright_test.py \
  --test-results test_output.txt
```

### Full Options

```bash
python selector_fixer.py \
  --selenium tests/selenium_test.py \
  --playwright tests/playwright_test.py \
  --test-results test_output.txt \
  --output tests/selenium_test.fixed.py \
  --report selector_report.txt \
  --api-key your-api-key-here
```

## Command Line Options

| Option | Required | Description |
|--------|----------|-------------|
| `--selenium` | Yes | Path to Selenium test file with broken selectors |
| `--playwright` | Yes | Path to Playwright test file with working selectors |
| `--test-results` | No | Path to test failure results (helps with context) |
| `--output` | No | Path for fixed Selenium file (default: `*.fixed.py`) |
| `--report` | No | Path for detailed report (default: `selector_fix_report.txt`) |
| `--api-key` | No | Anthropic API key (or use `ANTHROPIC_API_KEY` env var) |

## Example Workflow

### Step 1: You have broken Selenium tests

```python
# selenium_login_test.py
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_login():
    driver = webdriver.Chrome()
    driver.get("https://example.com/login")
    
    # These XPaths are broken!
    username = driver.find_element(By.XPATH, "/html/body/div[1]/form/div[1]/input")
    password = driver.find_element(By.XPATH, "/html/body/div[1]/form/div[2]/input")
    submit = driver.find_element(By.XPATH, "/html/body/div[1]/form/button")
    
    username.send_keys("user@example.com")
    password.send_keys("password123")
    submit.click()
```

### Step 2: You create Playwright tests with working selectors

```python
# playwright_login_test.py
from playwright.sync_api import sync_playwright

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com/login")
        
        # These selectors work!
        page.locator('#username').fill('user@example.com')
        page.locator('#password').fill('password123')
        page.locator('button[type="submit"]').click()
        
        browser.close()
```

### Step 3: Run the fixer

```bash
python selector_fixer.py \
  --selenium selenium_login_test.py \
  --playwright playwright_login_test.py
```

### Step 4: Review the output

The tool generates:
1. **Updated Selenium file** (`selenium_login_test.fixed.py`)
2. **Detailed report** (`selector_fix_report.txt`)

**Updated Selenium code:**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_login():
    driver = webdriver.Chrome()
    driver.get("https://example.com/login")
    
    # Updated with robust selectors!
    username = driver.find_element(By.XPATH, "//input[@id='username']")
    password = driver.find_element(By.XPATH, "//input[@id='password']")
    submit = driver.find_element(By.XPATH, "//button[@type='submit']")
    
    username.send_keys("user@example.com")
    password.send_keys("password123")
    submit.click()
```

**Report excerpt:**
```
================================================================================
SELENIUM SELECTOR FIX REPORT
================================================================================

Total Selectors Analyzed: 3

--------------------------------------------------------------------------------

1. SELECTOR MAPPING
--------------------------------------------------------------------------------
Broken XPath:      /html/body/div[1]/form/div[1]/input
Playwright Equiv:  #username
Suggested XPath:   //input[@id='username']
Alternative CSS:   #username

Reasoning: The broken absolute XPath is brittle and will break if DOM structure 
changes. The Playwright test uses the ID selector which is stable. Updated to 
a relative XPath that targets the ID attribute directly.
```

## Output Files

### Fixed Selenium Test
- Default location: `<original-name>.fixed.py`
- Contains your original test with updated selectors

### Detailed Report
- Default location: `selector_fix_report.txt`
- Includes:
  - Mapping of each broken selector to suggested replacement
  - Reasoning for each change
  - General recommendations for test stability

## Best Practices

### When Using This Tool

1. **Review Changes**: Always review the suggested changes before using them
2. **Test Thoroughly**: Run your updated tests to ensure they work
3. **Iterate if Needed**: If some selectors still don't work, you can run the tool again with updated test results

### For Better Results

1. **Provide Test Results**: Include test failure output for more context
2. **Keep Tests Similar**: Ensure Playwright and Selenium tests test the same functionality
3. **Use Descriptive Names**: Better code = better AI analysis

### Writing Better Selectors (General Advice)

The tool suggests selectors that follow these principles:

✅ **Good Selectors:**
- `//button[@id='submit']` - Uses stable ID
- `//input[@name='username']` - Uses stable name attribute
- `//div[@data-testid='login-form']` - Uses test-specific attributes
- `//button[contains(@class, 'btn-primary')]` - Flexible with classes

❌ **Avoid:**
- `/html/body/div[3]/div[1]/button` - Absolute paths break easily
- `//div[3]/span[2]` - Position-based selectors are brittle
- `//button[1]` - Index-based selectors change with DOM updates

## Troubleshooting

### "Error: anthropic package not installed"
```bash
pip install anthropic --break-system-packages
```

### "Error: API key not found"
Set your API key:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "Error parsing Claude's response"
This usually means the API had an issue. Try:
1. Check your API key is valid
2. Ensure you have API credits
3. Try again (temporary API issues)

### Selectors still not working after fix
1. Run the tool again with test failure results: `--test-results failures.txt`
2. Manually inspect the suggested selectors in browser DevTools
3. The DOM might have changed - update your Playwright test first, then re-run

## Advanced Usage

### Batch Processing Multiple Test Files

Create a simple shell script:

```bash
#!/bin/bash
# fix_all_tests.sh

for selenium_test in tests/selenium/*.py; do
    test_name=$(basename "$selenium_test" .py)
    playwright_test="tests/playwright/${test_name}.py"
    
    if [ -f "$playwright_test" ]; then
        echo "Fixing $test_name..."
        python selector_fixer.py \
          --selenium "$selenium_test" \
          --playwright "$playwright_test" \
          --output "tests/selenium_fixed/${test_name}.py" \
          --report "reports/${test_name}_report.txt"
    fi
done
```

### Using as a Python Module

```python
from selector_fixer import SelectorFixer

fixer = SelectorFixer(api_key="your-key")

selenium_code = Path("test.py").read_text()
playwright_code = Path("test_pw.py").read_text()

mappings = fixer.analyze_and_map_selectors(
    selenium_code,
    playwright_code
)

updated_code = fixer.update_selenium_code(
    selenium_code,
    mappings['mappings']
)

Path("test.fixed.py").write_text(updated_code)
```

## How It Works

1. **Extract Selectors**: Parses both test files to identify selectors
2. **AI Analysis**: Claude analyzes both tests to understand what they're testing
3. **Intelligent Mapping**: Maps broken Selenium selectors to working Playwright equivalents
4. **Suggest Improvements**: Provides robust XPath/CSS alternatives
5. **Update Code**: Automatically updates your Selenium test file
6. **Generate Report**: Creates detailed documentation of all changes

## Limitations

- Requires Anthropic API key (paid service)
- Works best when Playwright and Selenium tests are testing the same functionality
- May need manual review for complex selectors
- Cannot fix logical test errors, only selector issues

## Contributing

Feel free to enhance this tool! Some ideas:
- Support for other test frameworks (Cypress, WebDriverIO)
- Interactive mode for reviewing each change
- Integration with CI/CD pipelines
- Support for more selector patterns

## License

MIT License - Use freely in your projects!

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the generated report for specific selector issues
3. Consult Anthropic's Claude documentation for API questions

---

Happy testing! 🧪✨