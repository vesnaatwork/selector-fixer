#!/usr/bin/env python3
"""
Selenium Test Selector Fixer
Uses Claude AI to map working Playwright selectors to broken Selenium XPaths
and automatically update test files.
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import sys
import requests  # Add this import for Ollama API

class SelectorFixer:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2"):
        """Initialize the selector fixer with Ollama API"""
        self.ollama_url = ollama_url
        self.model = model

    def ollama_chat(self, prompt: str, system_prompt: str = None, temperature: float = 0.2, max_tokens: int = 2000) -> str:
        """Send prompt to local Ollama and return response text with options"""
        api_url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        try:
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                print(f"Error from Ollama API: {response.status_code}")
                print(response.text)
                return ""
        except Exception as e:
            print(f"Exception when calling Ollama API: {e}")
            return ""

    def extract_selectors_from_selenium(self, selenium_code: str) -> List[str]:
        """Extract XPath selectors from Selenium test code"""
        patterns = [
            r'find_element\([^,]+,\s*["\']([^"\']+)["\']\)',
            r'find_elements\([^,]+,\s*["\']([^"\']+)["\']\)',
            r'By\.XPATH,\s*["\']([^"\']+)["\']\)',
        ]
        
        selectors = []
        for pattern in patterns:
            matches = re.findall(pattern, selenium_code)
            selectors.extend(matches)
        
        return list(set(selectors))  # Remove duplicates
    
    def extract_selectors_from_playwright(self, playwright_code: str) -> List[str]:
        """Extract selectors from Playwright test code"""
        patterns = [
            r'locator\(["\']([^"\']+)["\']\)',
            r'get_by_[a-z]+\(["\']([^"\']+)["\']\)',
            r'\.click\(["\']([^"\']+)["\']\)',
            r'\.fill\(["\']([^"\']+)["\']\)',
        ]
        
        selectors = []
        for pattern in patterns:
            matches = re.findall(pattern, playwright_code)
            selectors.extend(matches)
        
        return list(set(selectors))
    
    def analyze_and_map_selectors(
        self, 
        selenium_code: str, 
        playwright_code: str, 
        test_results: str = None
    ) -> Dict:
        """Use Ollama to analyze both test files and map selectors"""
        prompt = f"""You are an expert in test automation, specifically Selenium and Playwright.

I have two test files testing the same functionality:
1. A Selenium test with broken XPath selectors
2. A Playwright test with working selectors

Your task is to:
1. Identify what each test is trying to do
2. Map the broken Selenium XPath selectors to their working Playwright equivalents
3. Suggest updated, robust XPath selectors for Selenium based on the Playwright selectors
4. Provide a complete mapping in JSON format

SELENIUM TEST (with broken selectors):
```python
{selenium_code}
```

PLAYWRIGHT TEST (working):
```python
{playwright_code}
```

{f"TEST FAILURE RESULTS:{chr(10)}{test_results}" if test_results else ""}

CRITICAL INSTRUCTIONS:
- Focus on creating ROBUST selectors that won't break easily
- Prefer IDs and data attributes over complex XPaths
- Use relative XPaths, not absolute ones
- Consider using contains() or starts-with() for dynamic attributes

Respond with ONLY a valid JSON object in this exact format (no markdown, no backticks):
{{
  "mappings": [
    {{
      "broken_selector": "the broken XPath from Selenium",
      "playwright_equivalent": "the working Playwright selector",
      "suggested_xpath": "improved XPath for Selenium",
      "suggested_css": "alternative CSS selector if applicable",
      "reasoning": "brief explanation of the mapping and why this selector is better"
    }}
  ],
  "general_recommendations": [
    "list of general recommendations for improving test stability"
  ]
}}

DO NOT include any text outside the JSON object. Your entire response must be valid JSON only."""

        response_text = self.ollama_chat(prompt)
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing Ollama's response: {e}")
            print(f"Response was: {response_text[:500]}")
            return None
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            return None
    
    def update_selenium_code(self, selenium_code: str, mappings: List[Dict]) -> str:
        """Update Selenium code with new selectors"""
        updated_code = selenium_code
        
        for mapping in mappings:
            broken = mapping.get('broken_selector', '')
            suggested = mapping.get('suggested_xpath', '')
            
            if broken and suggested:
                # Escape special regex characters
                broken_escaped = re.escape(broken)
                # Replace the selector in the code
                updated_code = re.sub(
                    f'["\']({broken_escaped})["\']',
                    f'"{suggested}"',
                    updated_code
                )
        
        return updated_code
    
    def generate_report(self, mappings: Dict, output_file: str = None):
        """Generate a detailed report of the selector mappings"""
        report = []
        report.append("=" * 80)
        report.append("SELENIUM SELECTOR FIX REPORT")
        report.append("=" * 80)
        report.append("")
        
        if mappings and 'mappings' in mappings:
            report.append(f"Total Selectors Analyzed: {len(mappings['mappings'])}")
            report.append("")
            report.append("-" * 80)
            
            for i, mapping in enumerate(mappings['mappings'], 1):
                report.append(f"\n{i}. SELECTOR MAPPING")
                report.append("-" * 80)
                report.append(f"Broken XPath:      {mapping.get('broken_selector', 'N/A')}")
                report.append(f"Playwright Equiv:  {mapping.get('playwright_equivalent', 'N/A')}")
                report.append(f"Suggested XPath:   {mapping.get('suggested_xpath', 'N/A')}")
                
                if mapping.get('suggested_css'):
                    report.append(f"Alternative CSS:   {mapping['suggested_css']}")
                
                report.append(f"\nReasoning: {mapping.get('reasoning', 'N/A')}")
                report.append("")
        
        if mappings and 'general_recommendations' in mappings:
            report.append("\n" + "=" * 80)
            report.append("GENERAL RECOMMENDATIONS")
            report.append("=" * 80)
            for rec in mappings['general_recommendations']:
                report.append(f"• {rec}")
        
        report_text = "\n".join(report)
        
        if output_file:
            Path(output_file).write_text(report_text)
            print(f"Report saved to: {output_file}")
        
        return report_text


def main():
    parser = argparse.ArgumentParser(
        description='Fix broken Selenium XPath selectors using working Playwright tests and Ollama'
    )
    parser.add_argument(
        '--selenium',
        required=True,
        help='Path to Selenium test file with broken selectors'
    )
    parser.add_argument(
        '--playwright',
        required=True,
        help='Path to Playwright test file with working selectors'
    )
    parser.add_argument(
        '--test-results',
        help='Path to test results file (optional)'
    )
    parser.add_argument(
        '--output',
        help='Path for updated Selenium test file (default: selenium_file.fixed.py)'
    )
    parser.add_argument(
        '--report',
        help='Path for detailed report (default: selector_fix_report.txt)'
    )
    parser.add_argument(
        '--ollama-url',
        default="http://localhost:11434",
        help='Ollama API URL (default: http://localhost:11434)'
    )
    parser.add_argument(
        '--model',
        default="llama3.2",
        help='Ollama model name (default: llama3)'
    )

    args = parser.parse_args()

    # Read input files
    try:
        selenium_code = Path(args.selenium).read_text()
        playwright_code = Path(args.playwright).read_text()
        test_results = Path(args.test_results).read_text() if args.test_results else None
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        sys.exit(1)

    # Initialize fixer
    print("Initializing Selector Fixer with Ollama...")
    fixer = SelectorFixer(ollama_url=args.ollama_url, model=args.model)

    # Analyze and map selectors
    print("\nAnalyzing tests and mapping selectors...")
    print("This may take a moment...\n")

    mappings = fixer.analyze_and_map_selectors(
        selenium_code,
        playwright_code,
        test_results
    )

    if not mappings:
        print("Error: Failed to analyze and map selectors")
        sys.exit(1)

    # Update Selenium code
    print("Updating Selenium test code...")
    updated_code = fixer.update_selenium_code(selenium_code, mappings.get('mappings', []))

    # Save updated code
    output_path = args.output or str(Path(args.selenium).with_suffix('.fixed.py'))
    Path(output_path).write_text(updated_code)
    print(f"✓ Updated Selenium test saved to: {output_path}")

    # Generate and save report
    report_path = args.report or 'selector_fix_report.txt'
    report = fixer.generate_report(mappings, report_path)
    print(f"✓ Detailed report saved to: {report_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    if mappings and 'mappings' in mappings:
        print(f"Selectors fixed: {len(mappings['mappings'])}")
        print(f"\nPreview of changes:")
        for i, mapping in enumerate(mappings['mappings'][:3], 1):
            print(f"\n{i}. {mapping.get('broken_selector', 'N/A')[:60]}...")
            print(f"   → {mapping.get('suggested_xpath', 'N/A')[:60]}...")

        if len(mappings['mappings']) > 3:
            print(f"\n   ... and {len(mappings['mappings']) - 3} more")

    print("\n✓ Done! Review the report and updated test file before running tests.")

if __name__ == '__main__':
    main()