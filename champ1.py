import requests
from requests.auth import HTTPBasicAuth

def list_github_repo_root(owner, repo, github_pat):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, auth=HTTPBasicAuth('', github_pat), headers=headers)

    if response.status_code == 200:
        print(f"Files in repo '{repo}':")
        for item in response.json():
            print(f"- {item['name']} ({item['type']})")
    else:
        print(f"Error {response.status_code}: {response.text}")

#Replace these with your real values
github_owner = "champ1710"
github_repo = "Devops-document-learning-"
github_pat = "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e"

list_github_repo_root(github_owner, github_repo, github_pat)

list_github_repo_root(github_owner, github_repo, github_pat)