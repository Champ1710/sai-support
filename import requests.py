import requests
import subprocess

SNYK_TOKEN = "308d2f8c-929d-4a14-bafb-b26dcbb2deec"
ORG = "bdhp-automation-test"
SEVERITY = "high"

def authenticate_snyk():
    url = "https://api.snyk.io/v1/user/me"
    headers = {
        "Authorization": f"token {SNYK_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("✅ Authenticated successfully!")
        print("👤 User info:", response.json())
        return True
    else:
        print("❌ Authentication failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return False

def read_images_from_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()
    return [line.strip() for line in lines if line.strip()]

def parse_image_metadata(image_full_path):
    # Example: bdhpcr.azurecr.io/images/bdhp-adt:5.9.0
    image_parts = image_full_path.split('/')
    image_with_tag = image_parts[-1]  # bdhp-adt:5.9.0
    image_name, version = image_with_tag.split(':')
    return image_name, version

def scan_images_with_snyk(image_list):
    for full_image in image_list:
        print(f"\n=== 🔍 Scanning Image: {full_image} ===")
        try:
            image_name, version = parse_image_metadata(full_image)
            tags = f"name={image_name},version={version}"

            result = subprocess.run(
                [
                    'snyk', 'container', 'monitor',
                    '--org', ORG,
                    '--tags', tags,
                    '--severity-threshold', SEVERITY,
                    full_image
                ],
                text=True,
                capture_output=True
            )

            print("--- ✅ STDOUT ---")
            print(result.stdout)
            print("--- ⚠️ STDERR ---")
            print(result.stderr)

            if result.returncode != 0:
                print(f"⚠️ Scan failed for image: {full_image}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error scanning image {full_image}:")
            print("--- STDOUT ---")
            print(e.stdout)
            print("--- STDERR ---")
            print(e.stderr)
        except Exception as ex:
            print(f"❌ Exception occurred while processing {full_image}: {str(ex)}")

if __name__ == "__main__":
    if authenticate_snyk():
        images = read_images_from_file("repos.txt")
        scan_images_with_snyk(images)
