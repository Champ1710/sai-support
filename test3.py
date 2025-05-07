import requests
from requests.auth import HTTPBasicAuth
import subprocess
import os

def list_github_repo_root(owner, github_pat):
    # Fetch all repositories for the given owner, with pagination handling
    url = f"https://api.github.com/users/{owner}/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    all_repos = []

    while url:
        response = requests.get(url, auth=HTTPBasicAuth('', github_pat), headers=headers)

        if response.status_code == 200:
            all_repos.extend(response.json())
            # Check for pagination
            if 'link' in response.headers and 'rel="next"' in response.headers['link']:
                url = response.headers['link'].split(';')[0][1:-1]
            else:
                url = None
        else:
            print(f"Error {response.status_code}: {response.text}")
            break

    # Iterate through all repositories and list their contents
    for repo in all_repos:
        repo_name = repo['name']
        print(f"\nListing files for repo: {repo_name}")
        list_repo_contents(owner, repo_name, github_pat)

def list_repo_contents(owner, repo, github_pat):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, auth=HTTPBasicAuth('', github_pat), headers=headers)

    if response.status_code == 200:
        found_dockerfile = False
        for item in response.json():
            print(f"- {item['name']} ({item['type']})")
            if item['name'].lower() == 'dockerfile':
                found_dockerfile = True
                print(f"Found Dockerfile in repo: {repo}")
                # Fetch Docker image (assuming Dockerfile exists)
                fetch_docker_image(owner, repo)
        if not found_dockerfile:
            print(f"No Dockerfile found in repo: {repo}")
    else:
        print(f"Error {response.status_code}: {response.text}")

def fetch_docker_image(owner, repo):
    """Fetch Docker image by building it from the Dockerfile in the repo."""
    try:
        # Clone the repository temporarily
        subprocess.run(["git", "clone", f"https://github.com/{owner}/{repo}.git"], check=True)

        # Change directory into the cloned repo
        os.chdir(repo)

        # Build the Docker image using the Dockerfile
        image_tag = f"{repo}:latest"
        subprocess.run(["docker", "build", "-t", image_tag, "."], check=True)

        # Optionally, you can push the image to a registry
        # subprocess.run(["docker", "push", image_tag], check=True)

        print(f"Docker image '{image_tag}' built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image for repo {repo}: {e}")
    finally:
        # Clean up by removing the cloned repository
        os.chdir("..")
        subprocess.run(["rm", "-rf", repo], check=True)

# Replace with your real values
github_owner = "champ1710"
github_pat = "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e"

list_github_repo_root(github_owner, github_pat)
