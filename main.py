import openai
import json
import os

# Initialize the OpenAI API client with the API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Mock weather tool (for demonstration purposes)
# In a real scenario, this could be a call to an external weather API
def get_weather(location):
    return f"The weather in {location} is sunny and 75°F."

# Define the tool (function) that will be made available to the model
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",  # The function name
        "description": "Get current temperature for a given location.",  # Function description
        "parameters": {
            "type": "object",  # The type of the parameter (JSON object)
            "properties": {
                "location": {
                    "type": "string",  # 'location' should be a string
                    "description": "City and country e.g. Paris, France"  # Description of the location parameter
                }
            },
            "required": ["location"],  # The 'location' parameter is required
            "additionalProperties": False  # No other properties allowed
        },
        "strict": True  # Ensures strict validation of function parameters
    }
}]

# Define the conversation messages that will be passed to the model
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather in Paris?"}  # User asks about the weather
]

# First API call: Request to OpenAI's API with the tool available
print("-------- First API Call --------")
response = openai.chat.completions.create(
    model="gpt-4",  # Use the latest model with function calling
    messages=messages,  # Provide the conversation context
    tools=tools,  # Specify the tools available for the model to use
)

# Print the response from the first call (before executing any tools)
print(response)

# Extract the message and any tool calls from the response
response_message = response.choices[0].message
tool_calls = response_message.tool_calls

# Check if any tool calls are made
if tool_calls:
    # Append the message to the conversation context for the second API call
    messages.append(response_message)

    # Define the available functions for the model to call
    available_functions = {
        "get_weather": get_weather,  # Map the function name to the actual Python function
    }

    # Process each tool call (function call)
    for tool_call in tool_calls:
        print(f"Tool Call: {tool_call}")  # Print out the tool call for debugging

        # Extract the function name and arguments
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]  # Get the function to call
        function_args = json.loads(tool_call.function.arguments)  # Parse the arguments

        # Get the 'location' argument from the function call
        location = function_args.get("location")

        # If the 'location' argument is present, call the function
        if location:
            # Call the function with the location parameter
            function_response = function_to_call(location=location)
            print(f"Function Response: {function_response}")  # Print the function response

            # Append the function response to the conversation
            messages.append(
                {
                    "role": "tool",  # Mark this message as a tool response
                    "name": function_name,
                    "content": function_response,
                    "tool_call_id": tool_call.id,  # Include the tool call ID for reference
                }
            )

# Second API call: Send the updated conversation with the tool's response back to OpenAI
print("-------- Second API Call --------")
second_response = openai.chat.completions.create(
    model="gpt-4",  # Use the latest model after the tool is called
    messages=messages,  # Provide the updated conversation context
)

# Print the response from the second API call
print(second_response)
print("-----")
print(second_response.choices[0].message.content)  # Print the final response message

