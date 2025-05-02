import os
import google.generativeai as genai

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyB9njJSYWlnVpfCGiP_u8DJE4_mmPrQEpQ"  # Replace with your actual API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def configure_gemini():
    """Configures the Gemini API."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_AI_STUDIO_API_KEY":
        print("Error: Please set your GOOGLE_API_KEY.")
        return False
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        return False

if not configure_gemini():
    exit()

MODEL_NAME = "gemini-1.5-pro-latest"

# Define the function to perform addition and subtraction
def calculate(operation: str, num1: float, num2: float) -> float:
    """Performs addition or subtraction."""
    if operation == "add":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    else:
        return "Invalid operation"

# Define function declaration
math_function_declaration = genai.types.FunctionDeclaration(
    name="calculate",
    description="Performs addition or subtraction.",
    parameters={
        "type": "object",
        "properties": {
            "operation": {"type": "string", "description": "The operation to perform: 'add' or 'subtract'."},
            "num1": {"type": "number", "description": "The first number."},
            "num2": {"type": "number", "description": "The second number."}
        },
        "required": ["operation", "num1", "num2"]
    }
)

# Create model with function support
model = genai.GenerativeModel(MODEL_NAME, tools=[math_function_declaration])
chat_session = model.start_chat()

def main():
    """Main interaction loop."""
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        response = chat_session.send_message(user_input)

        try:
            # Check if function call exists
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            arguments = dict(function_call.args)

            print(f"DEBUG: Function '{function_name}' called with arguments {arguments}")

            if function_name == "calculate":
                result = calculate(**arguments)
                print(f"Function Output: {result}")
                continue

        except (AttributeError, TypeError) as e:
            print(f"Gemini: {response.text}")

if __name__ == "__main__":
    main()