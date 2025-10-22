# Recruiter Voice Agent

A modular voice agent for recruitment screening calls using LiveKit, Deepgram STT, OpenAI LLM, and Cartesia TTS. The agent follows a strict recruitment script and automatically saves call results to CSV.

## Features

- **Strict Script Adherence**: Follows exact recruitment script without deviation
- **Real-time Data Collection**: Single tool for all data collection needs
- **Automatic Hangup**: Triggers when AI provides summary after saying goodbye
- **CSV Logging**: Saves call results with candidate details and interest status
- **Modular Design**: Easy to extend with new providers
- **Configurable Script**: Customize recruitment script variables

## Prerequisites

### 1. Install uv (Python Package Manager)

**Windows:**

```powershell
# Using PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Alternative (using pip):**

```bash
pip install uv
```

### 2. Verify Installation

```bash
uv --version
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd recruiting_agent
```

### 2. Install Dependencies

```bash
# Install all dependencies including dev dependencies
uv sync --dev

# Or install only production dependencies
uv sync
```

### 3. Download Required Files

```bash
# Download model files for VAD and turn detection
uv run python -m agent.main download-files
```

## Environment Setup

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
LIVEKIT_TOKEN=your-token

# Deepgram STT Configuration
DEEPGRAM_API_KEY=your-deepgram-api-key
DEEPGRAM_MODEL=nova-3

# OpenAI LLM Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Cartesia TTS Configuration
CARTESIA_API_KEY=your-cartesia-api-key
CARTESIA_VOICE_ID=your-voice-id
CARTESIA_MODEL=sonic-2
CARTESIA_FORMAT=wav
```

### 2. Configure Script Variables

Edit `src/agent/constants.py` to customize the recruitment script:

```python
@dataclass
class ScriptVariables:
    # Company details
    company_name: str = "Ultimate Outsourcing"
    recruiter_name: str = "Morgan"
    recruiter_title: str = "Recruitment Consultant"

    # Candidate details
    candidate_name: str = "John"

    # Job details
    role: str = "Software Developer"
    industry: str = "Technology"
    location: str = "Remote"
    salary: str = "$80,000 - $120,000"
```

## Usage

### 1. Start the Agent

```bash
# Connect to a specific Livekit playground room
uv run python -m agent.main connect --room "your-room-name"
```

### 2. Test the Agent

1. Open LiveKit Playground or your LiveKit client
2. Join the room specified in the command
3. The agent will automatically start the recruitment script
4. Follow the conversation flow
5. Results will be saved to `call_results.csv`

## Project Structure

```
src/agent/
├── __init__.py          # Main exports
├── main.py             # Entry point
├── config.py           # Settings and recruiter prompt
├── core.py             # Main agent logic
├── constants.py        # Script variables configuration
├── types.py            # Type definitions and protocols
├── session.py          # Session data management
├── tools.py            # AI function tools
└── providers/          # Extensible provider interfaces
    ├── __init__.py
    ├── stt.py          # Speech-to-text providers
    ├── llm.py          # Language model providers
    └── tts.py          # Text-to-speech providers
```

## Script Flow

The agent follows this exact script:

1. **Intro**: "Hi, {name}, this is {recruiter_name}, {recruiter_title} calling from {company_name}. Is it a good time to talk?"
2. **Reason**: "We're recruiting for a {role} {industry} in {location}, offering {salary}. Are you open to exploring this opportunity?"
3. **If NO**: Ask for reason, then provide appropriate closing
4. **If YES**: "Perfect, {name}. You'll hear from our Senior Consultant shortly. Thanks for your time today. Goodbye."
5. **Data Collection**: Automatically saves to CSV with candidate details and interest status

## Data Collection

The agent automatically collects and saves:

- **Candidate Name**: From script variables
- **Interest Status**: "Interested", "Not Interested", or "Asked for more details"
- **Summary**: Brief conversation summary
- **Timestamp**: When the call was completed

Results are saved to `call_results.csv` with the following format:

```csv
timestamp,candidate_name,interest_status,summary
2025-10-22T11:35:55.057029+00:00,John,Interested,Call completed by AI - candidate showed interest in the role
```

## API Keys Required

- **LiveKit**: For real-time communication
- **Deepgram**: For speech-to-text transcription
- **OpenAI**: For language model responses
- **Cartesia**: For text-to-speech synthesis

## License

This project is proprietary software owned by Hassan Aftab.

## Support

For technical support or questions, contact hassannaftabb@gmail.com.
