import requests
import re

# === CONFIGURATION ===
GITHUB_OWNER = "champ1710"  # Replace with your GitHub username
GITHUB_PAT = "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e"  # Replace with your actual token

# === HEADERS ===
HEADERS = {
    "Authorization": f"token {GITHUB_PAT}",
    "Accept": "application/vnd.github.v3+json"
}

def list_all_repos(owner):
    repos = []
    url = f"https://api.github.com/users/{owner}/repos?per_page=100"
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            repos.extend(response.json())
            # Pagination
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            print(f"❌ Failed to list repos: {response.status_code} - {response.text}")
            return []
    return [repo["name"] for repo in repos]

def list_files_and_find_dockerfiles(owner, repo, path=""):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    dockerfiles = []

    if response.status_code == 200:
        for item in response.json():
            if item["type"] == "dir":
                dockerfiles.extend(list_files_and_find_dockerfiles(owner, repo, item["path"]))
            elif item["type"] == "file" and item["name"].lower() == "dockerfile":
                dockerfiles.append(item["path"])
    else:
        print(f"⚠️ Error accessing {repo}/{path}: {response.status_code} - {response.text}")
    return dockerfiles

def get_dockerfile_base_image(owner, repo, filepath):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{filepath}"
    response = requests.get(url)
    if response.status_code == 200:
        matches = re.findall(r'^FROM\s+(.+)', response.text, re.MULTILINE)
        return matches
    else:
        print(f"⚠️ Could not fetch {filepath} from {repo}: {response.status_code}")
        return []

def main():
    repos = list_all_repos(GITHUB_OWNER)
    print(f"\n📦 Total Repos Found: {len(repos)}")

    for repo in repos:
        print(f"\n🔍 Scanning repo: {repo}")
        dockerfiles = list_files_and_find_dockerfiles(GITHUB_OWNER, repo)
        if dockerfiles:
            print(f"🧾 Dockerfiles found: {dockerfiles}")
            for path in dockerfiles:
                base_images = get_dockerfile_base_image(GITHUB_OWNER, repo, path)
                for img in base_images:
                    print(f"   📄 {repo}/{path} → FROM {img}")
        else:
            print("❌ No Dockerfile found.")

if __name__ == "__main__":
    main()
