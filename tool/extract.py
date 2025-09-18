import json
import yaml
import re
from urllib.parse import urlparse

def extract_from_har(har_data):
    simplified_requests = []

    for entry in har_data['log']['entries']:
        request = entry['request']
        url = request['url']

        if not url.startswith('http://192'):
            continue

        method = request['method']
        url_parts = urlparse(url)
        path = url_parts.path
        if url_parts.query:
            path += '?' + url_parts.query

        headers = {header['name']: header['value'] for header in request.get('headers', [])}

        body = None
        post_data = request.get('postData', {})
        if 'text' in post_data:
            body = post_data['text']

        simplified_requests.append({
            'method': method,
            'path': path,
            'headers': headers,
            'body': body
        })

    return simplified_requests

def convertYAML(ymlswaggerfile):
    with open(ymlswaggerfile, 'r', encoding='utf-8') as yaml_in:
        yaml_object = yaml.safe_load(yaml_in)
        jsonswaggerfile=json.dumps(yaml_object, default=str)
        jsonswaggerfile=json.loads(jsonswaggerfile)
    return jsonswaggerfile

def extract_from_openapi(openapi_data):
    simplified_requests = []

    base_path = openapi_data.get('servers', [{}])[0].get('url', '')

    for path, methods in openapi_data.get('paths', {}).items():
        path=re.sub(r'\{\w+\}', '1', path)
        for method, details in methods.items():
            simplified = {
                'method': method.upper(),
                'path': path,
                'headers': {},  # OpenAPI might define headers under parameters
                'body': None
            }

            # You can add more detailed handling for requestBody and parameters here
            if 'requestBody' in details:
                content = details['requestBody'].get('content', {})
                json_body = content.get('application/json', {}).get('example')
                if not json_body:
                    # Try extracting schema example
                    schema = content.get('application/json', {}).get('schema', {})
                    json_body = schema.get('example')
                if json_body:
                    simplified['body'] = json.dumps(json_body)

            simplified_requests.append(simplified)

    return simplified_requests

def parse_input_file(file):
    if file.lower().endswith(('.yml', '.yaml')):
        data=convertYAML(file)
    else:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    if 'log' in data and 'entries' in data['log']:  # It's a HAR file
        return extract_from_har(data)
    elif 'openapi' in data and 'paths' in data:  # It's an OpenAPI 3.0 spec
        return extract_from_openapi(data)
    else:
        raise ValueError("Unsupported file format")

# Example usage:
# simplified_requests = parse_input_file("input.har")
# simplified_requests = parse_input_file("openapi.json")
