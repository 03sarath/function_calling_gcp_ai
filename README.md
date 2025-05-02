# Food Recommendation System

A web application that recommends food based on weather conditions and user preferences using Gemini AI and Flask.

## Features

- Weather-based food recommendations
- View favorite foods
- Place food orders
- Interactive chat interface

## Prerequisites

- Python 3.8 or higher
- Node.js (for frontend development)
- OpenWeather API key
- Google Gemini API key

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd food-recommendation-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_API_KEY=your_gemini_api_key
```

5. Run the Flask backend:
```bash
python app.py
```

6. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

7. Install frontend dependencies:
```bash
npm install
```

8. Start the frontend development server:
```bash
npm start
```

9. Open your browser and navigate to `http://localhost:3000`

## Project Structure

```
food-recommendation-system/
├── app.py                 # Flask backend
├── weather_service.py     # Weather API service
├── food_preferences.json  # Food preferences data
├── requirements.txt       # Python dependencies
├── frontend/             # Frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── styles/       # CSS styles
│   │   └── App.js        # Main application
│   ├── package.json      # Frontend dependencies
│   └── public/           # Static files
└── README.md             # This file
```

## API Endpoints

- `POST /recommend`: Get food recommendations based on user input
  - Request body: `{ "message": "your message here" }`

## Usage

1. Enter your city name to get weather-based food recommendations
2. View your favorite foods
3. Place orders for recommended foods
4. Chat with the AI assistant for personalized recommendations

## Contributing

Feel free to submit issues and enhancement requests! 