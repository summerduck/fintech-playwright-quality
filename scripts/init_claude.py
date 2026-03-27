import json
import sys
from pathlib import Path

template_path = Path(".claude") / "settings.example.json"
output_path = Path(".claude") / "settings.local.json"
pwd = str(Path.cwd())

try:
    content = template_path.read_text(encoding="utf-8").replace("$PWD", pwd)
    json.loads(content)
    output_path.write_text(content, encoding="utf-8")
    print(f"Successfully created {output_path}")
    print(f"Replaced $PWD with: {pwd}")
except FileNotFoundError:
    print(f"Error: Could not find {template_path}", file=sys.stderr)
    print(
        "Make sure you run this script from the project root directory.",
        file=sys.stderr,
    )
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON after processing\n{e}", file=sys.stderr)
    sys.exit(1)
