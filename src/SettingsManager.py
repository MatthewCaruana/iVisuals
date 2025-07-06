import os
import json

class SettingsManager:
    def __init__(self):
        #load any existing settings currently stored in the settings.json file
        settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {}
    
    def update_settings(self, ui, setting, value):
        if setting in self.settings[ui]:
            self.settings[ui][setting] = value
            #ui.update_setting(setting, value)
            self.save_settings()
        else:
            print(f"Setting '{setting}' not found in settings.")

    def save_settings(self):
        settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
        with open(settings_path, 'w') as f:
            json.dump(self.settings, f, indent=4)
        print("Settings saved to", settings_path)

    def get_setting(self, ui, setting):
        if setting in self.settings[ui]:
            return self.settings[ui][setting]
        else:
            print(f"Setting '{setting}' not found in settings.")
            return None