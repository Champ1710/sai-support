import requests
import subprocess
from base64 import b64decode

# --- CONFIGURATION ---
GITHUB_TOKEN = 'ghp_xxxxxxxxxxxxxxxxx'  # Replace with your GitHub token
GITHUB_USER_OR_ORG = 'your-org-or-username'  # GitHub org or user
SNYK_TOKEN = 'your-snyk-token-here'  # Replace with your actual Snyk token

# --- HEADERS ---
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# --- GitHub API Base ---
API_URL = f"https://api.github.com/users/{GITHUB_USER_OR_ORG}/repos"

# --- FUNCTIONS ---

def get_repositories():
    repos = []
    page = 1
    while True:
        response = requests.get(f"{API_URL}?per_page=100&page={page}", headers=HEADERS)
        if response.status_code != 200:
            print("Error fetching repositories:", response.text)
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return [repo['full_name'] for repo in repos]

def get_dockerfile_from_repo(repo_full_name):
    dockerfile_paths = ['Dockerfile', 'docker/Dockerfile', 'Dockerfile.prod', 'Dockerfile.dev']
    for path in dockerfile_paths:
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            content = response.json()
            if content['encoding'] == 'base64':
                return b64decode(content['content']).decode('utf-8')
    return None

def extract_base_images(dockerfile_content):
    images = []
    for line in dockerfile_content.splitlines():
        line = line.strip()
        if line.upper().startswith('FROM'):
            parts = line.split()
            if len(parts) > 1:
                images.append(parts[1])
    return images

def scan_images_with_snyk(image_list):
    print("\n--- Running Snyk Container Scans ---")
    for image in image_list:
        print(f"\nScanning image: {image}")
        try:
            result = subprocess.run(
                ['snyk', 'container', 'test', image, f'--auth={SNYK_TOKEN}'],
                check=True,
                text=True,
                capture_output=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error scanning image {image}:\n{e.stderr}")

# --- MAIN ---

def main():
    all_images = []
    repos = get_repositories()
    print(f"\nFound {len(repos)} repositories.")

    for repo in repos:
        print(f"\nChecking {repo}")
        dockerfile = get_dockerfile_from_repo(repo)
        if dockerfile:
            print("Dockerfile found.")
            images = extract_base_images(dockerfile)
            print(f"Base images found: {images}")
            all_images.extend(images)
        else:
            print("No Dockerfile found.")

    all_images = list(set(all_images))  # Deduplicate
    print("\nCollected Docker images:")
    for img in all_images:
        print(f" - {img}")

    if all_images:
        scan_images_with_snyk(all_images)
    else:
        print("No Docker images to scan.")

if __name__ == "__main__":
    main()
