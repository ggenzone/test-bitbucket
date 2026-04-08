import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

file_path  = os.environ["FILE_PATH"]
branch     = os.environ["BRANCH"]
workspace  = os.environ["WORKSPACE"]
repo_slug  = os.environ["REPO_SLUG"]
token      = os.environ["BITBUCKET_TOKEN"]

encoded_path = urllib.parse.quote(file_path, safe="")
url = (
    f"https://api.bitbucket.org/2.0/repositories/"
    f"{workspace}/{repo_slug}/commits"
    f"?path={encoded_path}&include={urllib.parse.quote(branch, safe='')}&pagelen=1"
)

req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"WARNING: HTTP {e.code} for {file_path}", file=sys.stderr)
    sys.exit(0)
except Exception as e:
    print(f"WARNING: request failed – {e}", file=sys.stderr)
    sys.exit(0)

values = data.get("values", [])
if not values:
    print(f"NO_COMMITS")
    sys.exit(0)

date_str = values[0].get("date", "")
if not date_str:
    print(f"NO_DATE")
    sys.exit(0)

commit_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
cutoff_dt = datetime.now(timezone.utc) - timedelta(days=2)

print(date_str)
print("RECENT" if commit_dt >= cutoff_dt else "OLD")
