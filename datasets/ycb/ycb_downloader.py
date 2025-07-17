#Copyright 2015 Yale University - Grablab
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import json
import urllib.request
import subprocess
from tqdm import tqdm
output_directory = "./ycb"

# You can either set this to "all" or a list of the objects that you'd like to
# download.
#objects_to_download = "all"
#objects_to_download = ["002_master_chef_can", "003_cracker_box"]
objects_to_download = ["002_master_chef_can", "003_cracker_box","011_banana","012_strawberry","024_bowl","025_mug"]

# You can edit this list to only download certain kinds of files.
# 'berkeley_rgbd' contains all of the depth maps and images from the Carmines.
# 'berkeley_rgb_highres' contains all of the high-res images from the Canon cameras.
# 'berkeley_processed' contains all of the segmented point clouds and textured meshes.
# 'google_16k' contains google meshes with 16k vertices.
# 'google_64k' contains google meshes with 64k vertices.
# 'google_512k' contains google meshes with 512k vertices.
# See the website for more details.
#files_to_download = ["berkeley_rgbd", "berkeley_rgb_highres", "berkeley_processed", "google_16k", "google_64k", "google_512k"]
files_to_download = ["berkeley_processed", "berkeley_rgbd"]

# Extract all files from the downloaded .tgz, and remove .tgz files.
# If false, will just download all .tgz files to output_directory
extract = True

base_url = "http://ycb-benchmarks.s3-website-us-east-1.amazonaws.com/data/"
objects_url = base_url + "objects.json"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def fetch_objects(url):
    with urllib.request.urlopen(url) as response:
        data = response.read()
        return json.loads(data)["objects"]

def download_file(url, filename):
    with urllib.request.urlopen(url) as u:
        file_size = int(u.headers.get("Content-Length", 0))
        print(f"Downloading: {filename} ({file_size / 1_000_000:.2f} MB)")

        with open(filename, 'wb') as f:
            file_size_dl = 0
            block_sz = 65536
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                f.write(buffer)
                file_size_dl += len(buffer)
                percent = file_size_dl * 100. / file_size if file_size else 0
                print(f"\rDownloaded: {file_size_dl / 1_000_000:.2f} MB [{percent:.2f}%]", end='', flush=True)
        print()
def tgz_url(obj, file_type):
    if file_type in ["berkeley_rgbd", "berkeley_rgb_highres"]:
        return f"{base_url}berkeley/{obj}/{obj}_{file_type}.tgz"
    elif file_type == "berkeley_processed":
        return f"{base_url}berkeley/{obj}/{obj}_berkeley_meshes.tgz"
    else:
        return f"{base_url}google/{obj}_{file_type}.tgz"

def extract_tgz(filename, dir):
    try:
        subprocess.run(["tar", "-xzf", filename, "-C", dir], check=True)
        os.remove(filename)
    except Exception as e:
        print(f"Failed to extract {filename}: {e}")

def check_url(url):
    try:
        request = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(request):
            return True
    except Exception:
        return False

if __name__ == "__main__":
    objects = objects_to_download  # Or: fetch_objects(objects_url)

    for obj in tqdm(objects):
        if objects_to_download == "all" or obj in objects_to_download:
            for file_type in tqdm(files_to_download):
                url = tgz_url(obj, file_type)
                if not check_url(url):
                    print(f"Skipping: {url} not found")
                    continue

                suffix = "berkeley_meshes" if file_type == "berkeley_processed" else file_type
                filename = f"{output_directory}/{obj}_{suffix}.tgz"
                download_file(url, filename)

                if extract:
                    extract_tgz(filename, output_directory)