import requests
import time

def test_full_stack():
    url = "http://127.0.0.1:5000/craft_essences"
    params = {
        'filters': ['np_80plus', 'cost_12']
    }
    
    print(f"Sending GET to {url} with params: {params}")
    try:
        response = requests.get(url, params=params)
        print(f"Response Code: {response.status_code}")
        
        # Check if the response content seems filtered?
        # Difficult to parse HTML, but we should verify the LOGS.
        print("Request sent. Please check 'debug_search.log' for 'Filters=['np_80plus', 'cost_12']'")
        
        # We can also check if input checkboxes are 'checked' in the response HTML as a proxy
        if 'value="np_80plus" checked' in response.text:
            print("Response reflects 'np_80plus' is CHECKED -> App parsed params correctly.")
        else:
            print("Response does NOT show 'np_80plus' checked -> App failed to parse params.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_full_stack()
