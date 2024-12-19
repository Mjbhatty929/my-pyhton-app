import boto3
from PIL import Image, UnidentifiedImageError
import io

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Extract the source bucket and object key from the event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    destination_bucket = 'haji-lambda2'

    try:
        # Retrieve the image from the source S3 bucket
        print(f"Downloading {source_key} from bucket {source_bucket}")
        response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        image_data = response['Body'].read()

        # Open the image using PIL (Python Imaging Library)
        try:
            image = Image.open(io.BytesIO(image_data))
            print("Image successfully loaded")
        except UnidentifiedImageError:
            print(f"File {source_key} is not a valid image")
            return {
                'statusCode': 400,
                'body': f"File {source_key} is not a valid image"
            }

        # Convert the image to PNG format
        output_image = io.BytesIO()
        image.convert('RGBA').save(output_image, format='PNG')
        output_image.seek(0)  # Move the stream pointer to the beginning

        # Construct the destination key (change file extension to .png)
        destination_key = source_key.rsplit('.', 1)[0] + '.png'

        # Upload the converted image to the destination S3 bucket
        print(f"Uploading converted image to {destination_bucket}/{destination_key}")
        s3_client.put_object(
            Bucket=destination_bucket,
            Key=destination_key,
            Body=output_image,
            ContentType='image/png'
        )

        print(f"Successfully converted and uploaded {source_key} to {destination_bucket}/{destination_key}")
        return {
            'statusCode': 200,
            'body': f"Image converted and uploaded to {destination_bucket}/{destination_key}"
        }

    except Exception as e:
        print(f"Error processing file {source_key}: {e}")
        return {
            'statusCode': 500,
            'body': f"Error processing file: {str(e)}"
        }

