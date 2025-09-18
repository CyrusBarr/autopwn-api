import requests
from urllib.parse import urljoin

server_headers = ['Server', 'X-Powered-By']

def send_request(baseUrl, method, path, headers=None, body=None):
    url = urljoin(baseUrl, path)
    try:
        response = requests.request(method, url, headers=headers or {}, data=body, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"\nError sending request {url}: {e}")
        return None

def analyze_headers(baseUrl, req):
    response = send_request(baseUrl,req['method'], req['path'], req['headers'], req['body'])
    findings = []
    for header in server_headers:
        if header in response.headers:
            value = response.headers[header]
            findings.append((header, value))
    return findings

def test_server_header(baseUrl, captured_requests):
    print("Scanning for Server/X-Powered-By disclosure...")
    for req in captured_requests:
        results = analyze_headers(baseUrl, req)
        if results:
            print('='*100)
            print(f"\n[!] Potential Information Disclosure on {req['path']}")
            for header, value in results:
                print(f"    → {header}: {value}")
            return
        else:
            continue
            #print(f"\n[-] No disclosure detected on {req['path']}")
