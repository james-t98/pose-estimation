import os
import tempfile
import logging
from flask import Request, jsonify
from google.cloud import storage
import cv2

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize GCS client
storage_client = storage.Client()

def process_video(input_path, output_path):
    """
    Replace this with your real video processing logic (e.g., OpenCV + Mediapipe).
    """
    try:
        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            outfile.write(infile.read())
        logger.info("Video processing completed (placeholder)")
        return True
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return False

def main(request: Request):
    """
    HTTP entry point for Cloud Function or Cloud Run.
    Expects JSON body: { "bucket": "...", "file": "..." }
    """
    response = {
        "success": False,
        "input_file": None,
        "output_file": None,
        "message": ""
    }

    try:
        data = request.get_json(silent=True)

        if not data or 'bucket' not in data or 'file' not in data:
            response['message'] = "Missing 'bucket' or 'file' in request body."
            return jsonify(response), 400

        bucket_name = data['bucket']
        file_name = data['file']
        response["input_file"] = f"gs://{bucket_name}/{file_name}"

        logger.info(f"Received request to process gs://{bucket_name}/{file_name}")

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, 'input_video')
            output_path = os.path.join(tmpdir, 'output_video.mp4')

            # Download from GCS
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file_name)
            blob.download_to_filename(input_path)
            logger.info(f"Downloaded video to {input_path}")

            # Process the video
            success = process_video(input_path, output_path)

            if success:
                output_key = f"processed/{os.path.splitext(file_name)[0]}_processed.mp4"
                processed_blob = bucket.blob(output_key)
                processed_blob.upload_from_filename(output_path)
                logger.info(f"Uploaded processed video to {output_key}")

                response["success"] = True
                response["output_file"] = f"gs://{bucket_name}/{output_key}"
                response["message"] = "Video processed and uploaded successfully."
                return jsonify(response), 200
            else:
                response["message"] = "Video processing failed."
                return jsonify(response), 500

    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        response["message"] = f"Internal server error: {str(e)}"
        return jsonify(response), 500
