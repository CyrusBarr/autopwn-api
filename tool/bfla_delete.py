import requests
import re
from urllib.parse import urljoin 

methods_to_analyze = ['GET', 'PUT', 'POST']

wordlist1=[]
wordlist2=[]

with open('Wordlists/less_privilege.txt','r') as f:
    for word in f:
        wordlist1.append(word)

with open('Wordlists/higher_privilege.txt','r') as f:
    for word in f:
        wordlist2.append(word)

def contains_numeric(path):
    return bool(re.search(r'/\d+', path))

def contains_word(path):
    for word in wordlist1:
        word=word.strip()
        if word in path.strip('/').split('/'):
            return True
        
def modify_path(path, replacements):
    segments=path.strip('/').split("/")
    new_paths = []

    for id, segment in enumerate(segments):
        if contains_word(segment):
            for replacement in  replacements:
                replacement=replacement.strip()
                new_segments = segments.copy()
                new_segments[id] = replacement
                new_paths.append("/" + "/".join(new_segments))
    return new_paths

def send_request(baseUrl, method, path, headers=None, body=None):
    url = urljoin(baseUrl, path)
    try:
        response = requests.request(method, url, headers=headers or {}, data=body, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"\nError sending request {url}: {e}")
        return None

def is_bfla(original_response, final_response):
    # if not final_response:
    #     return False
    print(f'\nOriginal Response:{original_response.text[:200]}')
    print(f'\nFinal Response:{final_response.text[:200]}')
    if original_response.status_code == 200 and final_response.status_code != 200:    
        return True
    
    if  original_response.status_code != final_response.status_code:    
        return True 
    
    if original_response.status_code == 200 and final_response.status_code == 200:    
        return original_response.text != final_response.text
    
    return False

def test_bfla(baseUrl, captured_requests, auth_type, auth):
    for req in captured_requests:
        if auth_type:
            req['headers'][auth_type] = auth
        if req['method'] not in methods_to_analyze:
            #print(f"[-] {req['path']} does not meet criteria")
            continue

        if not contains_word(req['path']):
            #print(f"[-] {req['path']} does not meet criteria")
            continue

        if not contains_numeric(req['path']):
            #print(f"[-] {req['path']} does not meet criteria")
            continue
        
        print(f'\nSending request: {req['method']} {baseUrl}{req['path']}\n{req['body']}')
        original_response = send_request(baseUrl, req['method'], req['path'], req['headers'], req['body'])

        if 200 <= original_response.status_code < 300:
            modified_paths = modify_path(req['path'], wordlist2)

            for mod_path in modified_paths:
                print(f'\nSending request: DELETE {baseUrl}{mod_path}')
                delete_response = send_request(baseUrl, 'DELETE', mod_path, req['headers'], req['body'])
                if delete_response.status_code == 200:

                    print(f'\nSending request once more: {req['method']} {baseUrl}{req['path']}\n{req['body']}')
                    final_response = send_request(baseUrl, req['method'], req['path'], req['headers'], req['body'])

                    if is_bfla(original_response, final_response):
                        print(f"[!] BFLA detected on {req['method']} {req['path']} -> DELETE {mod_path}")
                    else:
                        continue
                        #print(f"[-] No BFLA detected on {req['path']}")
                else:
                    print(f"[-] Could not delete using {mod_path} {delete_response}")
        
        else:
            print(f'[-] Original request to {req['method']} {req['path']} failed!')
