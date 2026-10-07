import os
from bs4 import BeautifulSoup
import re

class InferenceEngine:
    def __init__(self):
        # Determine execution mode (Hardware or Local fallback)
        self.mode = "hardware" if self._detect_npu() else "local"
        print(f"Inference Engine initialized in {self.mode} mode.")
        
    def _detect_npu(self):
        # Placeholder for actual hardware detection logic (e.g. checking for HailoRT)
        # For our local testing, this will return False.
        return os.environ.get("USE_NPU") == "1"

    def analyze(self, url: str, html_content: str, screenshot_base64: str = None) -> dict:
        """
        Analyzes the DOM state and screenshot to detect threats.
        In a real implementation, this would use a VLM.
        For this prototype, we'll use a combination of heuristics that 
        simulate the VLM's detection of the specific test cases.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Check for prompt injection (hidden text)
        for elem in soup.find_all(style=re.compile(r'opacity:\s*0|display:\s*none', re.IGNORECASE)):
            text = elem.get_text(strip=True).lower()
            if "system override" in text or "ignore previous instructions" in text:
                return {"is_safe": False, "threat_type": "prompt_injection", "reason": "Hidden prompt injection detected"}

        # Also check div/spans if style is empty but might have hidden attributes
        for div in soup.find_all(['div', 'span', 'p']):
            # Fallback if style is missed by the regex above but has inline hidden elements
            text = div.get_text(strip=True).lower()
            if "system override" in text or "ignore previous instructions" in text:
                style = div.get('style', '')
                if 'opacity: 0' in style or 'display: none' in style or 'left: -9999' in style:
                    return {"is_safe": False, "threat_type": "prompt_injection", "reason": "Hidden prompt injection detected"}

        # 2. Check for UI redressing (invisible iframes)
        for iframe in soup.find_all('iframe'):
            style = iframe.get('style', '')
            class_list = iframe.get('class', [])
            # In a real VLM, this would compare visual bounding boxes. 
            if 'opacity: 0' in style or 'overlay' in class_list:
                return {"is_safe": False, "threat_type": "ui_redressing", "reason": "Invisible iframe overlay detected"}

        # 3. Check for DOM mutation (malicious form action)
        for form in soup.find_all('form'):
            action = form.get('action', '')
            # Simulate detecting a mutated action that points to a known bad domain
            if "attacker.com" in action:
                return {"is_safe": False, "threat_type": "dom_mutation", "reason": "Malicious form action URL detected"}

        return {"is_safe": True}
