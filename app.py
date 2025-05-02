from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Load food preferences
with open('food_preferences.json', 'r') as f:
    food_preferences = json.load(f)

# Define function declarations
tools = [
    {
        "function_declarations": [
            {
                "name": "get_weather_based_recommendation",
                "description": "Get food recommendation based on current weather in a city",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "city": {
                            "type": "STRING",
                            "description": "The city to get weather for"
                        }
                    },
                    "required": ["city"]
                }
            }
        ]
    },
    {
        "function_declarations": [
            {
                "name": "get_favorite_foods",
                "description": "Get list of favorite foods from preferences",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {},
                    "required": []
                }
            }
        ]
    },
    {
        "function_declarations": [
            {
                "name": "place_order",
                "description": "Place an order for a specific food item",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "food_name": {
                            "type": "STRING",
                            "description": "Name of the food to order"
                        }
                    },
                    "required": ["food_name"]
                }
            }
        ]
    }
]

# Create model with function support
model = genai.GenerativeModel('gemini-1.5-pro-latest', tools=tools)

def get_weather(city):
    """Get weather data for a city using WeatherAPI.com"""
    api_key = os.getenv('WEATHER_API_KEY')
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    try:
        params = {
            'key': api_key,
            'q': city,
            'aqi': 'no'
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        temperature = data['current']['temp_c']
        weather_condition = data['current']['condition']['text'].lower()
        
        # Updated weather categorization for Indian conditions
        if temperature < 20:
            weather_category = 'cold'
        elif temperature > 35:  # Changed from 25 to 35 for Indian summer
            weather_category = 'hot'
        elif 'rain' in weather_condition or 'drizzle' in weather_condition:
            weather_category = 'rainy'
        else:
            weather_category = 'mild'
            
        return {
            'temperature': temperature,
            'weather_condition': weather_condition,
            'weather_category': weather_category
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_weather_based_recommendation(city, user_preference=None):
    """Get food recommendation based on current weather and user preferences"""
    weather_data = get_weather(city)
    if not weather_data:
        return "Unable to fetch weather data"
    
    weather_category = weather_data['weather_category']
    matching_foods = [food for food in food_preferences['favorite_foods'] 
                     if food['weather_condition'] == weather_category]
    
    if user_preference:
        # If user mentions a specific food, find similar foods
        user_food = next((food for food in food_preferences['favorite_foods'] 
                         if food['name'].lower() == user_preference.lower()), None)
        
        if user_food:
            # Find foods with similar spice level and cuisine
            similar_foods = [food for food in matching_foods 
                           if (food['spice_level'] == user_food['spice_level'] or
                               food['cuisine'] == user_food['cuisine'])]
            if similar_foods:
                return {
                    "recommendation": similar_foods[0]['name'],
                    "weather": weather_data,
                    "reason": f"Recommended based on {weather_category} weather and similar to {user_preference}",
                    "description": similar_foods[0]['description']
                }
    
    if matching_foods:
        return {
            "recommendation": matching_foods[0]['name'],
            "weather": weather_data,
            "reason": f"Recommended based on {weather_category} weather",
            "description": matching_foods[0]['description']
        }
    return "No suitable food recommendations found"

def get_favorite_foods():
    """Get list of favorite foods"""
    return food_preferences['favorite_foods']

def place_order(food_name):
    """Place an order for a food item"""
    return {
        "status": "success",
        "message": f"Order placed for {food_name}",
        "order_id": "ORD-" + str(hash(food_name))[:8]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    city = request.form.get('city')
    user_preference = request.form.get('food_preference')
    
    if not city:
        return redirect(url_for('index'))
    
    try:
        chat = model.start_chat()
        prompt = f"What food do you recommend for {city}?"
        if user_preference:
            prompt += f" The user likes {user_preference}."
        
        response = chat.send_message(prompt)
        
        if hasattr(response.candidates[0].content.parts[0], 'function_call'):
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            arguments = dict(function_call.args)
            
            if function_name == "get_weather_based_recommendation":
                result = get_weather_based_recommendation(**arguments, user_preference=user_preference)
                return render_template('index.html', recommendation=result)
        
        return render_template('index.html', error="Failed to get recommendation")
    except Exception as e:
        return render_template('index.html', error=str(e))

@app.route('/get_favorites', methods=['POST'])
def get_favorites():
    try:
        chat = model.start_chat()
        response = chat.send_message("Show me my favorite foods")
        
        if hasattr(response.candidates[0].content.parts[0], 'function_call'):
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            
            if function_name == "get_favorite_foods":
                result = get_favorite_foods()
                return render_template('index.html', favorite_foods=result)
        
        return render_template('index.html', error="Failed to get favorite foods")
    except Exception as e:
        return render_template('index.html', error=str(e))

@app.route('/place_order', methods=['POST'])
def place_order():
    """Place an order for a food item"""
    food_name = request.form.get('food_name')
    if not food_name:
        return redirect(url_for('index'))
    
    try:
        chat = model.start_chat()
        response = chat.send_message(f"I want to order {food_name}")
        
        if hasattr(response.candidates[0].content.parts[0], 'function_call'):
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            arguments = dict(function_call.args)
            
            if function_name == "place_order":
                result = place_order_function(**arguments)
                return render_template('index.html', order_result=result)
        
        return render_template('index.html', error="Failed to place order")
    except Exception as e:
        return render_template('index.html', error=str(e))

def place_order_function(food_name):
    """Place an order for a food item"""
    return {
        "status": "success",
        "message": f"Order placed for {food_name}",
        "order_id": "ORD-" + str(hash(food_name))[:8]
    }

if __name__ == '__main__':
    app.run(debug=True) 