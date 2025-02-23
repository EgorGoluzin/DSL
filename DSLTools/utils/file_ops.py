import shutil
import os

def copy_template(src_dir, dest_dir, filename):
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(src_dir / filename, dest_dir / filename)

def generate_file(content, output_path):
    os.makedirs(output_path.parent, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)