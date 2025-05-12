import subprocess

# --- Configuration ---
SNYK_TOKEN = "308d2f8c-929d-4a14-bafb-b26dcbb2deec"
ORG = "bdhp-automation-test"
SEVERITY = "high"
REPOS_FILE = "repos.txt"

def authenticate_snyk():
    print("🔐 Authenticating with Snyk CLI...")
    try:
        result = subprocess.run(
            ["snyk", "auth", SNYK_TOKEN],
            text=True,
            capture_output=True
        )
        print("--- ✅ AUTH STDOUT ---")
        print(result.stdout)
        print("--- ⚠️ AUTH STDERR ---")
        print(result.stderr)
    except Exception as e:
        print(f"❌ Exception during Snyk auth: {str(e)}")

def read_images_from_file(filepath):
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def parse_image_metadata(image_full_path):
    try:
        # Example: bdhpcr.azurecr.io/images/bdhp-adt:5.9.0
        image_with_tag = image_full_path.split('/')[-1]  # bdhp-adt:5.9.0
        image_name, version = image_with_tag.split(':')
        return image_name, version
    except Exception as e:
        print(f"❌ Failed to parse image: {image_full_path} – {str(e)}")
        return None, None

def scan_image(image_full_path):
    image_name, version = parse_image_metadata(image_full_path)
    if not image_name or not version:
        return

    tags = f"name={image_name},version={version}"
    print(f"\n=== 🔍 Scanning: {image_full_path} ===")

    try:
        result = subprocess.run(
            [
                "snyk", "container", "monitor",
                "--org", ORG,
                "--tags", tags,
                "--severity-threshold", SEVERITY,
                image_full_path
            ],
            text=True,
            capture_output=True
        )

        print("--- ✅ STDOUT ---")
        print(result.stdout)
        print("--- ⚠️ STDERR ---")
        print(result.stderr)

        if result.returncode != 0:
            print(f"❌ Scan failed: {image_full_path}")
    except Exception as e:
        print(f"❌ Error running Snyk scan: {str(e)}")

if __name__ == "__main__":
    authenticate_snyk()
    images = read_images_from_file(REPOS_FILE)
    for img in images:
        scan_image(img)
