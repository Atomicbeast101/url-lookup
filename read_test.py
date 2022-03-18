# Imports
import requests.compat
import requests

# Attributes
TESTS = [
    ['test', 'test'], # Test
    ['facebook.com', 'api/v1/test'], # FOUND
    ['facebook.com', 'api/v1/test2'], # FOUND
    ['facebook.com', '/api/v1/test2'], # NOT_FOUND
    ['facebook.com', '/api/v1/test3'], # NOT_FOUND
    ['google.com:5000', 'api/v1/test'], # FOUND
    ['google.com:5000', 'api/v1/test3'], # FOUND
    ['google.com:655355', 'api/v1/test'], # Invalid input
    ['google.com:65535', '///ddd//'], # Invalid input
    ['google2.com', 'test1'], # NOT_FOUND (before running write_test.py)
    ['google2.com', 'api/test2'], # NOT_FOUND (before running write_test.py)
]

# Main
if __name__ == '__main__':
    print('INFO: Running some tests...')
    for test in TESTS:
        to_call = 'http://localhost/urlinfo/1/{}/{}'.format(
            requests.compat.quote_plus(test[0]), 
            requests.compat.quote_plus(test[1])
        )
        print(to_call)
        output = requests.get(to_call).text
        print(output)
    print('INFO: Finished all tests!')
