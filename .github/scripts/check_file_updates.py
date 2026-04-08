import base64, json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta
import yaml

def check_file(workspace, repo_slug, branch, file_path, credentials):
    encoded_path = urllib.parse.quote(file_path, safe="")
    url = (
        f"https://api.bitbucket.org/2.0/repositories/"
        f"{workspace}/{repo_slug}/commits"
        f"?path={encoded_path}&include={urllib.parse.quote(branch, safe='')}&pagelen=1"
    )

    encoded = base64.b64encode(credentials.encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {encoded}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"WARNING: HTTP {e.code} for {file_path}", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"WARNING: request failed – {e}", file=sys.stderr)
        return None, None

    values = data.get("values", [])
    if not values:
        return "NO_COMMITS", None

    date_str = values[0].get("date", "")
    if not date_str:
        return "NO_DATE", None

    commit_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=2)
    status = "RECENT" if commit_dt >= cutoff_dt else "OLD"
    return date_str, status

def main():
    account = os.environ["BITBUCKET_ACCOUNT"]
    token = os.environ["BITBUCKET_TOKEN"]
    credentials = f"{account}:{token}"

    settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "settings.yml")

    try:
        with open(settings_path) as f:
            settings = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: settings.yml not found at {settings_path}", file=sys.stderr)
        sys.exit(1)

    for repo in settings.get("repositories", []):
        repo_name = repo["name"]
        branch = repo["branch"]
        files = repo.get("files", [])

        try:
            workspace, repo_slug = repo_name.split("/", 1)
        except ValueError:
            print(f"ERROR: Invalid repository name '{repo_name}'. Expected format: 'workspace/repo-slug'", file=sys.stderr)
            continue

        print("──────────────────────────────────────────")
        print(f"Repository : {repo_name}")
        print(f"Branch     : {branch}")

        updated = False

        for file_path in files:
            print(f"  Checking file: {file_path}")

            commit_date, status = check_file(workspace, repo_slug, branch, file_path, credentials)

            if commit_date == "NO_COMMITS":
                print(f"    No commits found for {file_path} on branch {branch}")
                continue
            if commit_date == "NO_DATE":
                print(f"    Could not determine commit date for {file_path}")
                continue
            if commit_date is None:
                continue

            print(f"    Last commit date: {commit_date}")

            if status == "RECENT":
                print("    → File was updated within the last 2 days")
                updated = True
            else:
                print("    → File has not been updated in the last 2 days")

        if updated:
            print("RESULT: SEND A NOTIFICATION")
        else:
            print("RESULT: REPOSITORY UNCHANGED")


if __name__ == "__main__":
    main()
