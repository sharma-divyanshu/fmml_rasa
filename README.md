# Period Tracker with Voice Notes

A voice-enabled period tracking application that allows users to log their menstrual cycle information through voice notes. The application transcribes the voice notes, extracts relevant information (like flow, mood, and symptoms), and stores it in a database for future reference.

## Features

- Record voice notes to log period information
- Automatic transcription of voice notes
- Extraction of key information (flow, mood, symptoms)
- View recent logs and history
- Simple command-line interface

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fmml_rasa
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your ElevenLabs API key:
   - Get an API key from [ElevenLabs](https://elevenlabs.io/)
   - Create a `.env` file in the project root and add your API key:
     ```
     ELEVEN_LABS_API_KEY=your_api_key_here
     ```

## Usage

Run the application:
```bash
python -m period_tracker.app
```

### Available Commands

1. **Record a new voice note**:
   - Select option 1 and follow the prompts to record your voice note
   - The system will transcribe your note and extract relevant information

2. **View recent logs**:
   - Select option 2 to see your recent period logs

3. **Exit**:
   - Select option 3 to exit the application

## Data Storage

All data is stored in an SQLite database (`period_tracker.db` by default). Voice recordings are saved in the `data/audio` directory.

## Customization

You can customize the application by modifying the `period_tracker/config/settings.py` file. This includes:
- Keywords for extracting information from voice notes
- Default voice settings
- Database configuration

## Requirements

- Python 3.7+
- ElevenLabs API key
- Microphone (for voice recording)

## License

This project is licensed under the MIT License.