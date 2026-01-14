# Zenitheon Shop - Ecommerce Voice Agent

A modular voice agent for ecommerce shopping assistance using LiveKit, Deepgram STT, OpenAI LLM, and Cartesia TTS. The agent follows a structured shopping script, handles product recommendations, OTP verification, and automatically saves orders to CSV.

## Features

- **Structured Shopping Flow**: Follows exact Zenitheon Shop Whisper script
- **Product Inventory**: JSON-based product catalog (Hoodies, T-Shirts, Jackets)
- **OTP Verification**: Email-based OTP verification for order confirmation
- **Order Management**: Automatic order ID and tracking ID generation
- **CSV Logging**: Saves orders with customer details, products, and tracking information
- **Modular Design**: Easy to extend with new providers
- **Configurable Script**: Customize shopping script variables

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

# Email Configuration (for OTP sending)
# If not configured, OTP will be printed to console
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

### 2. Email Configuration (Optional)

For OTP email functionality, configure SMTP settings:

**Gmail Setup:**

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in `SMTP_PASSWORD`

**Note:** If email is not configured, OTP codes will be printed to the console for testing purposes.

### 3. Configure Script Variables

Edit `src/agent/constants.py` to customize the shopping script:

```python
@dataclass
class ScriptVariables:
    # Company details
    company_name: str = "Zenitheon"
    agent_name: str = "Shop Whisper"
    agent_title: str = "personal AI shopping assistant"
```

## Usage

### Option 1: Web Interface (Recommended)

1. **Start the Agent Worker** (in one terminal):

   ```bash
   uv run python -m agent.main dev
   ```

2. **Start the Web Server** (in another terminal):

   ```bash
   uv run python run.py
   ```

3. **Open Browser**:
   - Navigate to `http://localhost:5000`
   - Browse products
   - Click "Talk to Shop Whisper" to start a voice conversation
   - Allow microphone access when prompted

See [README_WEB.md](README_WEB.md) for detailed web interface documentation.

### Option 2: Direct LiveKit Connection

```bash
# Connect to a specific Livekit playground room
uv run python -m agent.main connect --room "your-room-name"
```

Then:

1. Open LiveKit Playground or your LiveKit client
2. Join the room specified in the command
3. The agent will automatically start the shopping script

### Conversation Flow

The agent follows this flow:

- Agent introduces itself
- Customer provides name
- Agent asks about product needs
- Customer mentions product category (Hoodie, T-Shirt, or Jacket)
- Agent presents product options
- Customer selects a product
- Agent requests email
- Agent sends OTP to email
- Customer provides OTP
- Agent confirms order and generates tracking ID
- Orders are saved to `orders.csv`

## Project Structure

```
src/
├── agent/              # Voice agent core
│   ├── __init__.py
│   ├── main.py        # Agent entry point
│   ├── config.py      # Settings and shop prompt
│   ├── core.py        # Main agent logic
│   ├── constants.py   # Script variables configuration
│   ├── types.py       # Type definitions and protocols
│   ├── session.py     # Session data management
│   ├── tools.py       # AI function tools
│   └── providers/     # Extensible provider interfaces
│       ├── __init__.py
│       ├── stt.py     # Speech-to-text providers
│       ├── llm.py     # Language model providers
│       └── tts.py     # Text-to-speech providers
└── web/               # Web interface
    ├── __init__.py
    ├── app.py         # Flask application
    ├── server.py      # Web server entry point
    ├── templates/     # HTML templates
    │   └── index.html
    └── static/        # Static assets
        ├── app.js     # Frontend JavaScript
        └── style.css  # Styles

inventory.json         # Product catalog
orders.csv            # Order records (generated)
web_main.py           # Web server entry point
```

## Script Flow

The agent follows this exact script:

1. **Agent Introduction**: "Welcome to Zenitheon, where style meets innovation. I am Shop Whisper, your personal AI shopping assistant. May I know who I am speaking with today?"
2. **Customer Introduction**: Customer provides their name
3. **Needs Assessment**: "It is a pleasure to meet you, [Customer Name]. How can I help you upgrade your wardrobe today? Are you looking for something specific?"
4. **Product Options**: Agent detects product category and retrieves 3 product options from inventory
5. **Product Selection**: Customer selects a product
6. **Email Request**: Agent requests email address for order confirmation
7. **OTP Verification**: Agent sends OTP to email, customer provides code
8. **Order Confirmation**: Agent generates order ID and tracking ID, confirms order
9. **Order Saved**: Order details saved to `orders.csv`

## Product Inventory

Products are stored in `inventory.json` with the following structure:

```json
{
  "products": {
    "Hoodie": [...],
    "T-Shirt": [...],
    "Jacket": [...]
  }
}
```

Each product has:

- `name`: Product name
- `description`: Product description
- `category`: Product category

## Data Collection

The agent automatically collects and saves:

- **Customer Name**: From conversation
- **Product Selection**: Selected product name
- **Email**: Customer email address
- **Order ID**: Generated order identifier (ORD-XXXXXXXX)
- **Tracking ID**: Generated tracking identifier (TRK-XXXXXXXXXXXX)
- **Summary**: Brief conversation summary
- **Timestamp**: When the order was placed

Results are saved to `orders.csv` with the following format:

```csv
timestamp,customer_name,product,email,order_id,tracking_id,summary
2025-10-22T11:35:55.057029+00:00,John Doe,The Stealth Bomber Jacket,john@example.com,ORD-ABC12345,TRK-XYZ123456789,Order completed successfully
```

## API Keys Required

- **LiveKit**: For real-time communication
- **Deepgram**: For speech-to-text transcription
- **OpenAI**: For language model responses
- **Cartesia**: For text-to-speech synthesis
- **SMTP** (Optional): For OTP email delivery

## License

This project is proprietary software owned by Hassan Aftab.

## Support

For technical support or questions, contact hassannaftabb@gmail.com.
