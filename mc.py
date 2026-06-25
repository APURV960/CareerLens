from google import genai

api_key = input("Enter your Gemini API key: ").strip()

client = genai.Client(api_key=api_key)

print("\nFetching available Gemini models...\n")

try:
    models = client.models.list()

    for model in models:
        print("=" * 60)
        print(f"Model Name: {model.name}")
        print(f"Display Name: {getattr(model, 'display_name', 'N/A')}")
        print(f"Input Token Limit: {getattr(model, 'input_token_limit', 'N/A')}")
        print(f"Output Token Limit: {getattr(model, 'output_token_limit', 'N/A')}")
        print(f"Supported Methods: {getattr(model, 'supported_generation_methods', 'N/A')}")

except Exception as e:
    print("Error fetching models:", e)