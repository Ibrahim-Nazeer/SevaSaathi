# SevaSaathi

A web-app ai chatbot that helps users discover and learn about government schemes tailored to their needs. Features an AI-powered chat interface and comprehensive scheme browsing capabilities.

## Features

- 🤖 **AI-Powered Chat Interface**: Ask questions about government schemes and get intelligent responses
- 🎨 **Beautiful UI**: Modern design with beige and sage green theme with orange accents
- 🔍 **Advanced Search & Filtering**: Find schemes by keywords and categories
- 📊 **Comprehensive Scheme Details**: View eligibility, benefits, application process, and more
- 📈 **Statistics Overview**: Quick insights into available schemes
- 💬 **Chat History**: Keep track of your conversations

## Project Structure

```
government_schemes_assistant/
│
├── main.py                    # Main Streamlit application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── README.md                 # This file
│
├── config/
│   └── settings.py           # Configuration settings and constants
│
├── ui/
│   ├── styles.py            # CSS styles and theming
│   └── components.py        # Reusable UI components
│
├── utils/
│   ├── api_client.py        # Gemini AI API client
│   └── data_loader.py       # Data loading utilities
│
├── services/
│   └── chat_handler.py      # Chat handling service
│
└── data/scheme_data.json  # Government schemes data
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd government_schemes_assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Edit .env file
   add your Gemini API key, api timeout and max tries
   ```

4. **Prepare your data**
   - Place your government schemes data in `data/scheme_data.json`
   - The JSON should contain an array of scheme objects with the following structure:
   ```json
   [
     {
       "name": "Scheme Name",
       "category": "Category",
       "description": "Scheme description",
       "target_audience": ["audience1", "audience2"],
       "eligibility": ["criteria1", "criteria2"],
       "benefits": ["benefit1", "benefit2"],
       "application_process": ["step1", "step2"],
       "documents_required": ["doc1", "doc2"],
       "official_website": "https://example.com"
     }
   ]
   ```

## Usage

1. **Run the application**
   ```bash
   streamlit run main.py
   ```

2. **Access the application**
   - Open your browser and go to `http://localhost:8501`

3. **Features to explore**
   - Browse schemes by category
   - Search for specific schemes
   - Chat with the AI assistant
   - View detailed scheme information

## Configuration

### Environment Variables (.env)

- `GEMINI_API_KEY`: Your Google Gemini API key
- `APP_TITLE`: Application title (default: "SevaSaathi")
- `DEBUG_MODE`: Enable debug mode (default: False)
- `SCHEMES_DATA_PATH`: Path to schemes data file
- `API_TIMEOUT`: API request timeout in seconds
- `MAX_RETRIES`: Maximum API retry attempts

### Theme Customization

The application uses a custom theme defined in `ui/styles.py`:
- **Primary Color**: Beige (#F5F5DC)
- **Secondary Color**: Sage Green (#9CAF88)
- **Accent Color**: Orange (#FF6B35)
- **Text Color**: Brown (#8B4513)

## API Integration

The application integrates with Google's Gemini AI API for intelligent chat responses. Make sure to:

1. Get a Gemini API key from Google AI Studio
2. Add it to your `.env` file
3. Ensure you have appropriate API quotas

## Data Format

The schemes data should be in JSON format with the following structure for each scheme:

```json
{
  "name": "string",
  "category": "string",
  "description": "string",
  "target_audience": ["string"],
  "eligibility": ["string"],
  "benefits": ["string"],
  "application": "string",
  "benefits":"string",
  "Official Website":"string",
  "Application Form":"string",
  "Order\/Notice":"string",
}
```
