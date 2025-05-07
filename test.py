import os
import time
import requests
import subprocess
from base64 import b64decode
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
load_dotenv()

# --- Retrieve Tokens from Environment ---
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
SNYK_TOKEN = os.getenv('SNYK_TOKEN')
GITHUB_USER_OR_ORG = os.getenv('GITHUB_USER_OR_ORG')

if not SNYK_TOKEN or not GITHUB_TOKEN or not GITHUB_USER_OR_ORG:
    print("❌ Missing required environment variables.")
    exit(1)

# --- Headers ---
GITHUB_HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

SNYK_HEADERS = {
    'Authorization': f'token {SNYK_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.api+json'
}


# --- Snyk Functions ---
def get_snyk_org_id():
    url = "https://api.snyk.io/rest/orgs"
    res = requests.get(url, headers=SNYK_HEADERS)
    res.raise_for_status()
    orgs = res.json()["data"]
    print("✅ Snyk Orgs:")
    for org in orgs:
        print(f"- {org['attributes']['name']} (ID: {org['id']})")
    return orgs[0]["id"]


def import_image_to_snyk(org_id, image_name, tag="latest"):
    url = f"https://api.snyk.io/rest/orgs/{org_id}/integrations/docker-hub/container-registries/library/images"
    payload = {
        "data": {
            "type": "container-image",
            "attributes": {
                "image": image_name,
                "tag": tag
            }
        }
    }
    response = requests.post(url, headers=SNYK_HEADERS, json=payload)
    if response.status_code == 201:
        print(f"✅ Triggered scan for {image_name}:{tag}")
    else:
        print(f"❌ Failed to import {image_name}:{tag} → {response.status_code}")
        print(response.text)


# --- GitHub Functions ---
def get_github_repositories():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{GITHUB_USER_OR_ORG}/repos?per_page=100&page={page}"
        res = requests.get(url, headers=GITHUB_HEADERS)
        if res.status_code != 200:
            print("❌ GitHub API error:", res.text)
            break
        data = res.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return [repo["full_name"] for repo in repos]


def get_dockerfile_content(repo_full_name):
    docker_paths = ['Dockerfile', 'docker/Dockerfile', 'Dockerfile.prod', 'Dockerfile.dev']
    for path in docker_paths:
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
        res = requests.get(url, headers=GITHUB_HEADERS)
        if res.status_code == 200:
            content = res.json()
            return b64decode(content['content']).decode('utf-8')
    return None


def extract_base_images(dockerfile):
    images = []
    for line in dockerfile.splitlines():
        if line.strip().upper().startswith('FROM'):
            parts = line.split()
            if len(parts) > 1:
                images.append(parts[1])
    return images


def scan_images_with_snyk_cli(images):
    print("\n🔍 Snyk CLI Scans:")
    for image in images:
        print(f"🛠️ Scanning: {image}")
        try:
            subprocess.run(['snyk', 'container', 'test', image],
                           check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error scanning {image}:\n{e.stderr}")


# --- Main Flow ---
def main():
    print("🚀 Starting Snyk Docker Image Scan")
    org_id = get_snyk_org_id()

    all_images = []
    repos = get_github_repositories()
    print(f"📚 Found {len(repos)} repos.")

    for repo in repos:
        print(f"\n🔍 Checking repo: {repo}")
        dockerfile = get_dockerfile_content(repo)
        if dockerfile:
            images = extract_base_images(dockerfile)
            if images:
                print(f"📦 Images found: {images}")
                all_images.extend(images)
        else:
            print("⚠️ No Dockerfile found.")

    all_images = list(set(all_images))  # Deduplicate

    # Trigger Snyk API Scan
    for img in all_images:
        if ":" in img:
            name, tag = img.split(":", 1)
        else:
            name, tag = img, "latest"
        import_image_to_snyk(org_id, name, tag)

    # Optionally run CLI scan
    scan_images_with_snyk_cli(all_images)


if __name__ == "__main__":
    main()


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
github_owner = "Hillrom-Enterprise"
github_repo = "bdhp-iqecs"
github_pat = "ghp_your_actual_token_here"

list_github_repo_root(github_owner, github_repo, github_pat)