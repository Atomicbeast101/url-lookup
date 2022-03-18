# Imports
import requests.compat
import requests

# Attributes
TEST = [
    ['google2.com', 'test1'], # VALID
    ['google2.com', 'api/test2'], # VALID
#    ['google2.com:5000000', 'test3'], # INVALID
    ['facebook2.com', 'test/test2'], # VALID
    ['facebook2.com:25', 'test/test3'], # VALID
#    ['facebook2.com', 'test////test4//'] # INVALID
]

# Main
if __name__ == '__main__':
    print('INFO: Running some tests...')
    output = requests.post('http://localhost/urladd/1', json={ 'data': TEST }).json()
    print(output)
    print('INFO: Finished all tests!')
