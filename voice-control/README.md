# Voice Control for Windows

A browser voice interface plus a small local Windows companion. The companion uses only Python's standard library.

## Requirements
- Windows 10 or Windows 11
- Python 3 installed (python.org); during setup, enable "Add Python to PATH"
- Current Google Chrome or Microsoft Edge
- Microphone permission for the website

## Start
1. Download `voice_assistant.py` from this folder.
2. Open the downloaded file's folder in File Explorer.
3. Click the address bar, type `cmd`, and press Enter.
4. Run: `py voice_assistant.py`
5. Keep the terminal window open. Copy the pairing code it displays.
6. Open the website: https://aliahmedstot-afk.github.io/robotic-hand/voice-control/
7. Paste the code into "Connect your laptop", then click Connect.
8. Allow microphone access and press the microphone button to speak.

## Supported voice commands
- Open Notepad / Calculator / File Explorer / Chrome / Edge / Settings
- Volume up / Volume down / Mute
- Switch window / Show desktop
- Scroll up / Scroll down / Press Enter
- Type followed by text (up to 500 characters)
- Search for followed by a phrase
- Close current window (the website asks for confirmation)

## Security notes
- The companion binds only to 127.0.0.1 (your own laptop), not your network.
- It accepts requests only from this project's GitHub Pages origin and requires a random pairing code printed locally.
- It has a fixed allowlist. It does not run shell commands supplied by speech, delete files, or shut down the PC.
- Stop it with Ctrl+C when finished. Never share your pairing code.
- This is an early version; test simple commands first and review what the browser recognized before sending a command.
