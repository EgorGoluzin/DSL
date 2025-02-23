# implementations/rbnf_extractor.py
import re


class RBNFExtractor:
    def __init__(self, content: str):
        self.content = content

    def extract(self) -> dict:
        return {
            "terminals": self._extract_terminals(),
            "nonterminals": self._extract_nonterminals(),
            "axiom": self._extract_axiom()
        }

    def _extract_terminals(self):
        return re.findall(r'<(\w+)>\s*::=', self.content)

    def _extract_nonterminals(self):
        return list(set(re.findall(r'(\w+)\s*::=', self.content)))

    def _extract_axiom(self):
        match = re.search(r'AXIOM:\s*(\w+)', self.content)
        return match.group(1) if match else None


class VirtExtractor:
    def __init__(self, content: str):
        self.content = content

    def extract(self) -> dict:
        return {
            "terminals": self._extract_terminals(),
            "nonterminals": self._extract_nonterminals(),
            "axiom": self._extract_axiom()
        }

    def _extract_terminals(self):
        return re.findall(r'<(\w+)>\s*::=', self.content)

    def _extract_nonterminals(self):
        return list(set(re.findall(r'(\w+)\s*::=', self.content)))

    def _extract_axiom(self):
        match = re.search(r'AXIOM:\s*(\w+)', self.content)
        return match.group(1) if match else None


class UMLExtractor:
    def __init__(self, content: str):
        self.content = content

    def extract(self) -> dict:
        return {
            "terminals": self._extract_terminals(),
            "nonterminals": self._extract_nonterminals(),
            "axiom": self._extract_axiom()
        }

    def _extract_terminals(self):
        return re.findall(r'<(\w+)>\s*::=', self.content)

    def _extract_nonterminals(self):
        return list(set(re.findall(r'(\w+)\s*::=', self.content)))

    def _extract_axiom(self):
        match = re.search(r'AXIOM:\s*(\w+)', self.content)
        return match.group(1) if match else None
