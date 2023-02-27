from pathlib import Path
from collections import Counter
import re

vault_path = Path().home() /'test/Notes' #/ "Cloud/@Home/Notes"
dry_run = False

markdown_files = []
image_filenames = dict()
name_counter = Counter()
multilink_images = []

pattern = r"!\[\[(Pasted|Screenshot).*?\.png]]"
rgx = re.compile(pattern)

# Loop through markdown files, check if they contain pasted screenshots
for path in vault_path.rglob("*.md"):
    with open(path) as f:
        markdown = f.read()

    matches = list(rgx.finditer(markdown))

    if not matches:
        continue
    markdown_files.append((path, matches))

    print(len(matches))

    for i, m in enumerate(matches):
        current_name = markdown[m.span()[0] : m.span()[1]]
        # IF image is linked multiple times, it will be skipped
        if current_name in image_filenames:
            multilink_images.append(current_name)
            continue

        namefmt = "![[Screenshot {} {}{}.png]]".format
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
        current_name = m.string[m.span()[0] : m.span()[1]]
        if current_name not in image_filenames:
            continue
        print(f"Changing link: {current_name} --> {image_filenames[current_name]}")
        markdown = markdown.replace(current_name, image_filenames[current_name])
    if not dry_run:
        path.unlink()
        with open(path, 'w') as f:
            f.write(markdown)
for path in vault_path.rglob("*.png"):
    key = f"![[{path.name}]]"
    if key in image_filenames:
        new_filename = image_filenames[key][3:-2]
        print(f"Renaming: {path.name} --> {new_filename}")
        if not dry_run:
            path.rename(new_filename)

print(f"Updates {len(markdown_files)} md files and {len(image_filenames)} images")
