# tui_module.py
class TUI:
    alphabet = "ABCDEFGHJKLMNPQRSTVWXYZ"

    def __init__(self, value):
        self.value = value

    def is_valid(self):
        import re

        regex = re.compile(r"[0-9]{7}[A-Z]")
        if not regex.match(self.value):
            return False

        ctrl_key = sum(int(digit) * (len(self.value[:-1]) - index) for index, digit in enumerate(self.value[:-1])) % 23
        
        return self.value[-1] == list(TUI.alphabet)[ctrl_key]