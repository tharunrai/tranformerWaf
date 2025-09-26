import requests
import json
import time

BACKEND_URL = 'http://localhost:5000/api/analyze'

def test_request(method, path, body='', headers=None):
    if headers is None:
        headers = {'User-Agent': 'Test Client'}

    data = {
        'method': method,
        'path': path,
        'headers': headers,
        'body': body,
        'query_params': {}
    }

    try:
        response = requests.post(BACKEND_URL, json=data)
        result = response.json()
        print(f"Request: {method} {path}")
        print(f"Result: {'ATTACK' if result['is_attack'] else 'BENIGN'} - {result.get('attack_type', 'N/A')}")
        print("-" * 50)
        return result
    except Exception as e:
        print(f"Error testing {method} {path}: {e}")
        return None

def run_tests():
    print("🚀 Starting WAF Attack Tests\n")

    # Test benign requests
    print("Testing benign requests:")
    test_request('GET', '/home')
    test_request('POST', '/login', 'username=test&password=test')
    test_request('GET', '/dashboard')

    time.sleep(1)

    # Test attacks
    print("Testing attacks:")
    test_request('GET', "/login?user=admin' OR '1'='1")
    test_request('POST', '/search', "<script>alert('xss')</script>")
    test_request('GET', '/admin.php?id=1 UNION SELECT username,password FROM users')
    test_request('GET', '/../../../etc/passwd')

    print("✅ Tests completed!")

if __name__ == "__main__":
    run_tests()