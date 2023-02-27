from pathlib import Path
from collections import Counter
import re


def deconstruct_link(match):
    s = match.string[match.span()[0] : match.span()[1]][3:-2]
    if "|" in s:
        s, width = s.split("|")
    else:
        width = None
    return s, width


def create_link(name, width):
    if width:
        name = f"{name}|{width}"
    return f"![[{name}]]"


vault_path = Path().home() / "Cloud/@Home/Notes"
dry_run = False

markdown_files = []
image_filenames = dict()
name_counter = Counter()
multilink_images = []

pattern = r"!\[\[(Pasted|Screenshot).*?\.png.*?]]"
rgx = re.compile(pattern)

# Loop through markdown files, check if they contain pasted screenshots
for path in vault_path.rglob("*.md"):
    with open(path) as f:
        markdown = f.read()

    matches = list(rgx.finditer(markdown))

    if not matches:
        continue
    markdown_files.append((path, matches))

    for i, m in enumerate(matches):
        current_name, _ = deconstruct_link(m)
        # IF image is linked from multiple markdown files, it will be skipped
        if current_name in image_filenames:
            multilink_images.append(current_name)
            continue

        namefmt = "Screenshot {} {}{}.png".format
        proposed_name = namefmt(path.stem, i + 1, "")
        # If name already exists, add a letter to end of filename
        if name_counter[proposed_name] > 0:
            c = 0
            while name_counter[proposed_name] > 0:
                proposed_name = namefmt(path.stem, i + 1, chr(ord("A") + c))
                c += 1
            name_counter.update([proposed_name])
        else:
            name_counter.update([proposed_name])

        image_filenames[current_name] = proposed_name

# Remove images with multiple links
for name in multilink_images:
    print(f"File {current_name} linked multiple times, skipping")
    del image_filenames[current_name]

# Update md file content
for path, matches in markdown_files:
    with open(path) as f:
        markdown = f.read()
    for m in matches:
        current_name, width = deconstruct_link(m)
        if current_name not in image_filenames:
            continue
        print(f"Changing link: {current_name} --> {image_filenames[current_name]}")
        markdown = markdown.replace(
            create_link(current_name, width),
            create_link(image_filenames[current_name], width),
        )
    if not dry_run:
        path.unlink()
        with open(path, "w") as f:
            f.write(markdown)

# Rename images
for path in vault_path.rglob("*.png"):
    if path.name in image_filenames:
        new_filename = image_filenames[path.name]
        print(f"Renaming: {path.name} --> {new_filename}")
        if not dry_run:
            path.replace(path.parent / new_filename)

print(f"Updated {len(markdown_files)} md files and {len(image_filenames)} images")
