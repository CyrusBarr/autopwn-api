import requests
import re
from urllib.parse import urljoin

params=[]
with open('Wordlists/param-wordlist1.txt','r') as f:
    for word in f:
        params.append(word)

def identification(o_endpoint):
    m_endpoints=[]
    matches=re.findall(r'(?<=/)(\d+)(?=/|$)|^(\d+)(?=/)',o_endpoint)
    if bool(matches):
        for match in matches:
            number_str = match[0] if match[0] else match[1]
            num_increment=int(number_str)+1
            m_endpoint = re.sub(rf'(?<=/){number_str}(?=/|$)|^{number_str}(?=/)', str(num_increment), o_endpoint, count=1)
            m_endpoints.append(m_endpoint)
        return m_endpoints
    
def send_request(baseUrl, method, path, headers=None, body=None):
    url = urljoin(baseUrl, path)
    try:
        response = requests.request(method, url, headers=headers or {}, data=body, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"\nError sending request {url}: {e}")
        return None

def if_bola(original_response, manipulated_response, o_path, m_path,ids):
    if original_response.status_code == 200 and manipulated_response.status_code == 200:
        for id in ids:
            id=id.strip()
            matches=re.findall(r'(?<=/)(\d+)(?=/|$)|^(\d+)(?=/)',o_path)
            if bool(matches):
                for match in matches:
                    number_match = match[0] if match[0] else match[1]
                    original_id_value=re.search(r'[\'"]'+re.escape(id)+r'[\'"]:[\'"]*'+re.escape(number_match)+r'[\'"]*',original_response.text)
                    manipulated_id_value=re.search(r'[\'"]'+re.escape(id)+r'[\'"]:[\'"]*\s*[A-Za-z-0-9-]+[\'"]*',manipulated_response.text)
                    if not original_id_value or not manipulated_id_value:
                            continue
                    elif id in manipulated_response.text and original_id_value.group() != manipulated_id_value.group():
                        print("="*100+"\n")
                        print("Original Response " + o_path + ":\b")
                        print(original_response.text + "\n")
                        print("-"*100+"\n")
                        print("Manipulated Response " + m_path + ":\b")
                        print(manipulated_response.text + "\n")
                        print("[!] Vulnerability Detected in " + id)
                        print('[!] Reason:',original_id_value.group(0),manipulated_id_value.group(0))
                        print("="*100+"\n")
                        return True
            else:
                continue
                #print('[-] Valid Response but No Vulnerability Detected')

    if original_response.text != manipulated_response.text:
        #print("[-] No Vulnerability Detected")
        return False
 
    if manipulated_response.status_code == 403 or manipulated_response.status_code == 401:
        #print("[-] Error: No Vulnerability Detected")
        return False
    
    #print("[-] Default - No Vulnerability Detected")
    return False


def test_num_bola(baseUrl, captured_requests, auth_type, auth):
    for req in captured_requests:
        if auth_type:
            req['headers'][auth_type] = auth
        o_request_path=baseUrl+req['path']
        m_endpoints=identification(req['path'])
        try:
            if m_endpoints is None:
                #print(f'[-] {req['path']}: endpoint did not match criteria')
                continue
            else:
                for m_endpoint in m_endpoints:
                    try:
                        original_response=send_request(baseUrl, req['method'], req['path'], req['headers'], req['body'])
                        manipulated_response=send_request(baseUrl, req['method'], m_endpoint, req['headers'], req['body'])
                        if not original_response or not manipulated_response:
                            continue
                        if_bola(original_response, manipulated_response, req['path'], m_endpoint,params)
                    except requests.exceptions.ConnectTimeout as err:
                        print(f'HOST UNREACHABLE: {o_request_path}')
        except TypeError as e:
            print(f"Error: {e}")