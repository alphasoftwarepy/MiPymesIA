import urllib.request
import json
import os
import dotenv

dotenv.load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print("Testing API Key:", api_key[:15] + "..." + api_key[-15:] if api_key else "None")

if not api_key:
    print("Error: No API Key found in .env")
    exit(1)

req = urllib.request.Request(
    'https://api.openai.com/v1/chat/completions',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    },
    data=json.dumps({
        'model': 'gpt-4o-mini',
        'messages': [{'role': 'user', 'content': 'hi'}],
        'max_tokens': 5
    }).encode('utf-8'),
    method='POST'
)

print("Sending request to OpenAI API...")
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        print("Success! Response:")
        print(res['choices'][0]['message']['content'])
except Exception as e:
    print("Error during request:", e)
    if hasattr(e, 'read'):
        print("Response Body:", e.read().decode('utf-8'))
