import os
import re
import requests
from textwrap import dedent

REPO = os.getenv("GITHUB_REPOSITORY", "YOUR_USERNAME/YOUR_USERNAME")
OWNER = REPO.split("/")[0]

API = f"https://api.github.com/users/{OWNER}/repos?sort=updated&per_page=8"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

resp = requests.get(API, headers=HEADERS, timeout=30)
resp.raise_for_status()
repos = resp.json()

# Filtrar: no forks, no repo de perfil
filtered = [
    r for r in repos
    if not r.get("fork") and r.get("name").lower() != OWNER.lower()
]

# Priorizar repos con topic 'featured'
featured = [r for r in filtered if 'featured' in (r.get('topics') or [])]
others = [r for r in filtered if r not in featured]
ordered = featured + others

md_lines = []
for r in ordered[:6]:
    name = r.get("name", "")
    desc = r.get("description") or "Sin descripción"
    stars = r.get("stargazers_count", 0)
    url = r.get("html_url")
    line = f"- <a href=\"{url}\"><b>{name}</b></a> — {desc} ⭐{stars}"
    md_lines.append(line)

content_new = "\n".join(md_lines) if md_lines else "Aún no hay repositorios publicados. Sube tu primer proyecto y este bloque se actualizará automáticamente."

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r"(<!-- LATEST-REPOS:START -->)(.*?)(<!-- LATEST-REPOS:END -->)"
replacement = dedent(f"""
    
    <!-- LATEST-REPOS:START -->
    {content_new}
    <!-- LATEST-REPOS:END -->
    """).strip("\n")

new_readme = re.sub(pattern, replacement, readme, flags=re.S)

if new_readme != readme:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)
    print("README actualizado.")
else:
    print("Sin cambios.")
