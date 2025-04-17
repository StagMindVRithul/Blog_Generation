import re
import boto3
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(topic:str)->str:

    body = {
        "prompt":f"Write a 250 words blog on the topic {topic}.",
        'max_gen_len':512,
        'temperature':0.6,
        'top_p':0.9
    }

    try:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            config = botocore.config.Config(
                read_timeout=300,
                retries = {
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )
        )
        response = bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-70b-instruct-v1:0",accept="application/json",contentType="application/json")
        response_content = response.get('body').read().decode('utf-8')
        response_data = json.loads(response_content)
        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog due to: {e}")
        return ""
    

def save_blog_details_s3(s3_key,s3_bucket,generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(
            Bucket = s3_bucket,
            Key = s3_key,
            Body = generate_blog
        )
        print("Code saved successfully to S3")
    except Exception as e:
        print(f"Error saving the code to S3: {e}")
        return ""
    

def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event['body'])
    blog_topic = event['topic']
    generate_blog = blog_generate_using_bedrock(blog_topic)
    if generate_blog:
        current_time = datetime.now().strftime("%H%M:%S")
        s3_key = f"blogs-output/{current_time}.txt"
        s3_bucket = "bloggenerationaws"
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)


    else:
        print("No blog generated")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Blog generation completed')
    }
