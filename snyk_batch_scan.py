import os
import time
import requests
import subprocess
from base64 import b64decode
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

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

# --- Lock for thread-safe access to shared `all_images` ---
all_images_lock = Lock()

# --- Snyk Functions ---
def get_snyk_org_id():
    try:
        url = "https://api.snyk.io/rest/orgs"
        res = requests.get(url, headers=SNYK_HEADERS)
        res.raise_for_status()
        orgs = res.json()["data"]
        print("✅ Snyk Orgs:")
        for org in orgs:
            print(f"- {org['attributes']['name']} (ID: {org['id']})")
        return orgs[0]["id"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Snyk org: {e}")
        exit(1)

def import_image_to_snyk(org_id, image_name, tag="latest"):
    try:
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
    except requests.exceptions.RequestException as e:
        print(f"❌ Error triggering Snyk scan for {image_name}:{tag}: {e}")

# --- GitHub Functions ---
def get_github_repositories():
    repos = []
    page = 1
    while True:
        try:
            url = f"https://api.github.com/users/{GITHUB_USER_OR_ORG}/repos?per_page=100&page={page}"
            res = requests.get(url, headers=GITHUB_HEADERS)
            res.raise_for_status()
            data = res.json()
            if not data:
                break
            repos.extend(data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching repositories: {e}")
            break
    return [repo["full_name"] for repo in repos]

def get_dockerfile_content(repo_full_name):
    docker_paths = ['Dockerfile', 'docker/Dockerfile', 'Dockerfile.prod', 'Dockerfile.dev']
    for path in docker_paths:
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
        try:
            res = requests.get(url, headers=GITHUB_HEADERS)
            res.raise_for_status()
            content = res.json()
            # Print the Dockerfile path in the desired format with escaped backslashes
            print(f'dockerfilePath ""\\repos\\github-hillrom\\bdhp\\bdhp-adt\\ADTService\\Dockerfile"""')
            return b64decode(content['content']).decode('utf-8')
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching Dockerfile for {repo_full_name}: {e}")
            continue
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
            subprocess.run(['snyk', 'container', 'test', image], check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error scanning {image}:\n{e.stderr}")

# --- Main Flow ---
def main():
    print("Starting Snyk Docker Image Scan")
    org_id = get_snyk_org_id()

    all_images = []
    repos = get_github_repositories()
    print(f"📚 Found {len(repos)} repos.")

    # Use ThreadPoolExecutor to process repositories in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        for repo in repos:
            futures.append(executor.submit(process_repo, repo, org_id, all_images))

        # Wait for all futures to complete
        for future in futures:
            future.result()  # This will raise an exception if one occurs in the thread

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

def process_repo(repo, org_id, all_images):
    print(f"\n🔍 Checking repo: {repo}")
    dockerfile = get_dockerfile_content(repo)
    if dockerfile:
        images = extract_base_images(dockerfile)
        if images:
            print(f"📦 Images found: {images}")
            with all_images_lock:
                all_images.extend(images)
    else:
        print("⚠️ No Dockerfile found.")

if __name__ == "__main__":
    main()
