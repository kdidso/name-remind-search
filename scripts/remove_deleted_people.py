import re
import json
from pathlib import Path

# --- CONFIG ---
REPO_ROOT = Path(".")
DELETE_FILE = REPO_ROOT / "data" / "Names_to_Delete.txt"
PEOPLE_FILE = REPO_ROOT / "people.js"


def read_names(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def last_first_to_display(name: str) -> str:
    if "," not in name:
        return name.strip()

    last, first = [part.strip() for part in name.split(",", 1)]
    if not first:
        return last
    return f"{first} {last}".strip()


def load_people():
    if not PEOPLE_FILE.exists():
        raise FileNotFoundError(f"Missing people.js: {PEOPLE_FILE}")

    text = PEOPLE_FILE.read_text(encoding="utf-8")

    match = re.search(r'window\.people\s*=\s*(\[[\s\S]*?\]);', text)
    if not match:
        raise ValueError("Could not find window.people array in people.js")

    json_text = match.group(1)

    # Parse JS array as JSON
    people = json.loads(json_text)

    return people, text


def save_people(original_text, people):
    new_array = json.dumps(people, indent=2)

    updated_text = re.sub(
        r'window\.people\s*=\s*\[[\s\S]*?\];',
        f'window.people = {new_array};',
        original_text
    )

    PEOPLE_FILE.write_text(updated_text, encoding="utf-8")


def main():
    raw_names = read_names(DELETE_FILE)
    names_to_delete = {last_first_to_display(n) for n in raw_names}

    people, original_text = load_people()

    remaining = []
    removed = []

    for p in people:
        if p["name"] in names_to_delete:
            removed.append(p["name"])
        else:
            remaining.append(p)

    save_people(original_text, remaining)

    print(f"Removed {len(removed)} people from people.js")
    if removed:
        print("Removed names:")
        for name in sorted(removed, key=str.casefold):
            print(f"- {name}")


if __name__ == "__main__":
    main()
