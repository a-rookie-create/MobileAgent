import os
import re
import time
import subprocess
import shlex
import unicodedata
from .controller import Controller

_APP_ACTIVITY_PATTERNS = (
    ('settings|system settings', 'com.android.settings/.Settings'),
    ('audio recorder', 'com.dimowner.audiorecorder/com.dimowner.audiorecorder.app.welcome.WelcomeActivity'),
    ('files', 'com.google.android.documentsui/com.android.documentsui.files.FilesActivity'),
    ('markor', 'net.gsantner.markor/net.gsantner.markor.activity.MainActivity'),
    ('simple sms messenger|simple sms', 'com.simplemobiletools.smsmessenger/com.simplemobiletools.smsmessenger.activities.MainActivity'),
    ('simple calendar pro|simple calendar', 'com.simplemobiletools.calendar.pro/com.simplemobiletools.calendar.pro.activities.MainActivity'),
    ('simple gallery pro|simple gallery', 'com.simplemobiletools.gallery.pro/com.simplemobiletools.gallery.pro.activities.MainActivity'),
    ('simple draw pro', 'com.simplemobiletools.draw.pro/com.simplemobiletools.draw.pro.activities.MainActivity'),
    ('pro expense|pro expense app', 'com.arduia.expense/com.arduia.expense.ui.MainActivity'),
    ('broccoli|broccoli app|broccoli recipe app|recipe app', 'com.flauschcode.broccoli/com.flauschcode.broccoli.MainActivity'),
    ('osmand', 'net.osmand/net.osmand.plus.activities.MapActivity'),
    ('tasks|tasks app|tasks.org:', 'org.tasks/com.todoroo.astrid.activity.MainActivity'),
    ('open tracks sports tracker|activity tracker|open tracks|opentracks', 'de.dennisguse.opentracks/de.dennisguse.opentracks.TrackListActivity'),
    ('joplin|joplin app', 'net.cozic.joplin/.MainActivity'),
    ('vlc|vlc app|vlc player', 'org.videolan.vlc/.gui.MainActivity'),
    ('retro music|retro|retro player', 'code.name.monkey.retromusic/.activities.MainActivity'),
    ('clock', 'com.google.android.deskclock/com.android.deskclock.DeskClock'),
    ('chrome|google chrome', 'com.android.chrome/com.google.android.apps.chrome.Main'),
    ('contacts', 'com.google.android.contacts/com.android.contacts.activities.PeopleActivity'),
    ('camera', 'com.android.camera2/com.android.camera.CameraLauncher'),
)

def _activity_for_app(app_name: str) -> str:
    app_name = app_name.lower().strip()
    if '/' in app_name:
        return app_name
    for pattern, activity in _APP_ACTIVITY_PATTERNS:
        if re.fullmatch(pattern, app_name):
            return activity
    raise ValueError(f"Unknown app name for open_app: {app_name}")

def _adb_text_format(text: str) -> str:
    """Prepares text for use with adb input text, matching AndroidWorld."""
    to_escape = [
        '\\',
        ';',
        '|',
        '`',
        '\r',
        ' ',
        "'",
        '"',
        '&',
        '<',
        '>',
        '(',
        ')',
        '#',
        '$',
    ]
    for char in to_escape:
        text = text.replace(char, '\\' + char)
    normalized_text = unicodedata.normalize('NFKD', text)
    return normalized_text.encode('ascii', 'ignore').decode('ascii')

def _split_words_and_newlines(text: str):
    """Split lines of text into individual words and newline chars."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        words = line.split(' ')
        for j, word in enumerate(words):
            if word:
                yield word
            if j < len(words) - 1:
                yield '%s'
        if i < len(lines) - 1:
            yield '\n'

class AndroidController(Controller):
    def __init__(self, adb_path):
        self.adb_path = adb_path

    def get_screenshot(self, save_path):
        command = self.adb_path + " shell rm /sdcard/screenshot.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(0.5)
        command = self.adb_path + " shell screencap -p /sdcard/screenshot.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(0.5)
        command = self.adb_path + f" pull /sdcard/screenshot.png {shlex.quote(save_path)}"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        
        if not os.path.exists(save_path):
            return False
        else:
            return True

    def tap(self, x, y):
        command = self.adb_path + f" shell input tap {x} {y}"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def open_app(self, app_name):
        activity = _activity_for_app(app_name)
        command = self.adb_path + f" shell am start -n {activity}"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)

    def type(self, text):
        for word in _split_words_and_newlines(text):
            if word == '\n':
                command = self.adb_path + " shell input keyevent 66"
            else:
                formatted = _adb_text_format(word)
                command = self.adb_path + f" shell input text {shlex.quote(formatted)}"
            subprocess.run(command, capture_output=True, text=True, shell=True)

    def slide(self, x1, y1, x2, y2):
        command = self.adb_path + f" shell input swipe {x1} {y1} {x2} {y2} 500"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def back(self):
        command = self.adb_path + " shell input keyevent 4"
        subprocess.run(command, capture_output=True, text=True, shell=True)

    def home(self):
        command = self.adb_path + " shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
        subprocess.run(command, capture_output=True, text=True, shell=True)
