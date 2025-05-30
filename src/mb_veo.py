import time
from google import genai
from google.genai.types import GenerateVideosConfig
import os

# Ensure environment variables are set or configure manually
# project_id = "your-project-id"
# location = "your-gcp-region" # e.g., us-central1
# genai.configure(vertexai=True, project=project_id, location=location)

# Initialize the GenAI Client for Vertex AI
try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing client. Ensure GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, and GOOGLE_GENAI_USE_VERTEXAI are set, or gcloud auth is configured: {e}")
    exit()

# --- Configuration ---
# Use the specific Veo 3 model name. This might be 'veo-3.0-generate-preview'
# or another identifier provided by Google during the preview.
# Fallback to a generic Veo model name if Veo 3 specific one isn't confirmed.
model_name = "veo-3.0-generate-preview" # Or "veo-2.0-generate-001", etc. check documentation
prompt_text = "A futuristic cityscape at sunset with flying vehicles and neon lights, cinematic style."
output_gcs_bucket_name = "your-gcs-bucket-name" # Replace with your bucket name
output_gcs_prefix = "veo3_outputs/my_video"    # Desired path prefix in the bucket
output_gcs_uri = f"gs://{output_gcs_bucket_name}/{output_gcs_prefix}"

try:
    print(f"Starting video generation with model: {model_name}")
    operation = client.models.generate_videos(
        model=model_name,
        prompt=prompt_text,
        config=GenerateVideosConfig(
            aspect_ratio="16:9", # Common aspect ratios: "16:9", "9:16"
            # video_length_sec=8, # Optional: Desired video length in seconds (check model limits)
            output_gcs_uri=output_gcs_uri,
            # You can add other parameters like 'negative_prompt', 'seed_number' etc.
            # Refer to the official documentation for all available options.
        )
    )

    print(f"Video generation operation started. Name: {operation.operation.name}")
    print("Polling for completion (this may take several minutes)...")

    while not operation.done():
        time.sleep(30)  # Wait for 30 seconds before checking status
        operation.refresh() # Refresh operation status
        if operation.metadata:
            print(f"Operation status: {operation.metadata.state}") # e.g., STATE_RUNNING, STATE_SUCCEEDED
        else:
            print("Processing...")

    if operation.error:
        print(f"Error during video generation: {operation.error.message}")
    elif operation.result and hasattr(operation.result, 'generated_videos') and operation.result.generated_videos:
        generated_video_uri = operation.result.generated_videos[0].video.uri
        print(f"Video generated successfully! Output GCS URI: {generated_video_uri}")
    else:
        print("Operation finished but no video URI found or an unknown error occurred.")
        if operation.result:
            print(f"Raw result: {operation.result}")


except AttributeError as e:
    print(f"AttributeError: {e}. This might be due to an incorrect model name, an issue with the SDK version, or 'output_gcs_uri' not being set if required.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")