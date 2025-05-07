import os
import requests
from requests.auth import HTTPBasicAuth
import time

def get_rate_limit(github_pat):
    url = "https://api.github.com/rate_limit"
    headers = {
        "Authorization": f"token {github_pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rate_limit = response.json()
        remaining = rate_limit['resources']['core']['remaining']
        reset_time = rate_limit['resources']['core']['reset']
        return remaining, reset_time
    else:
        print(f"Failed to get rate limit info: {response.status_code}")
        return None, None

def wait_for_rate_limit_reset(reset_time):
    # Wait until the reset time (convert Unix timestamp to seconds)
    wait_seconds = reset_time - int(time.time()) + 10  # adding a buffer of 10 seconds
    print(f"Rate limit exceeded. Waiting for {wait_seconds} seconds.")
    time.sleep(wait_seconds)

def list_all_repos(owner, github_pat):
    repos = []
    url = f"https://api.github.com/users/{owner}/repos"
    headers = {"Authorization": f"token {github_pat}", "Accept": "application/vnd.github.v3+json"}

    while url:
        response = requests.get(url, headers=headers)
        
        # Check if rate limit is exceeded
        if response.status_code == 403:
            remaining, reset_time = get_rate_limit(github_pat)
            if remaining == 0:
                wait_for_rate_limit_reset(reset_time)
                continue  # Retry the request after waiting
            
        if response.status_code == 200:
            repos += response.json()
            if 'link' in response.headers and 'rel="next"' in response.headers['link']:
                url = response.headers['link'].split(';')[0][1:-1]
            else:
                url = None
        else:
            print(f"❌ Failed to list repos: {response.status_code} - {response.text}")
            break
    return [repo["name"] for repo in repos]

# Example call
github_owner = "champ1710"
github_pat = "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e"  # Use a secure method to store the token

repos = list_all_repos(github_owner, github_pat)
print(repos)
