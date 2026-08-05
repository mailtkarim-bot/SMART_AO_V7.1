"""
SMART_AO V7 - Piège Rules Engine
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class PiegeRule:
    id: str
    name: str
    description: str
    pattern: str
    severity: str
    category: str
    
    def match(self, text: str) -> bool:
        return bool(re.search(self.pattern, text, re.IGNORECASE))

class PiegeRulesEngine:
    DEFAULT_RULES = [
        PiegeRule("CCAG_001", "CCAG 10%/5% manquant", 
                 "Clauses CCAG sans mention des seuils", 
                 r"(CCAG).*?(?<!10%|5%)", "HIGH", "CCAG"),
        PiegeRule("PAB_001", "PAB -20%/-30% manquant",
                 "PAB sans mention des pénalités",
                 r"(PAB).*?(?<!20%|30%)", "CRITICAL", "PAB"),
    ]
    
    def __init__(self):
        self.rules = self.DEFAULT_RULES
    
    def analyze_document(self, text: str) -> Dict[str, List[str]]:
        findings = {}
        for rule in self.rules:
            if rule.match(text):
                if rule.category not in findings:
                    findings[rule.category] = []
                findings[rule.category].append(rule.id)
        return findings
