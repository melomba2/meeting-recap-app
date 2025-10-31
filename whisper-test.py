import sys
sys.path.append('/Users/michaellombard/ai-projects/meetings-app/src-python')

from remote_whisper_client import RemoteWhisperClient

print("Creating client...")
client = RemoteWhisperClient(whisper_host="http://192.168.68.10:5000")

print("Testing connection...")
result = client.check_connection()
print(f"check_connection() returned: {result}")

if result:
    print("✅ Connection successful!")
    models = client.get_available_models()
    print(f"Models: {models}")
else:
    print("❌ Connection failed")