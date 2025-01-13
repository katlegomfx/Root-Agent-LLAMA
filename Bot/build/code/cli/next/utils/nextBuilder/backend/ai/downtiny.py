# utils\nextBuilder\backend\ai\downtiny.py
import sys
import os
import shutil

sys.path.append(os.getcwd())

from huggingface_hub import hf_hub_download

from utils.shared import app_name  # nopep8

repo_id = 'TinyLlama/TinyLlama-1.1B-python-v0.1'
filename = 'ggml-model-q4_0.gguf'
repo_name = repo_id.split('/')[-1]
file_type = filename.split(".")[-1]
base_path = f"{repo_name}.{file_type}"

check = os.path.exists(os.path.join(app_name, 'public', base_path))

if not check:
    model_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        cache_dir=os.path.join(app_name, 'public')
    )

    base = model_path.replace('\\', '/').split('public/')[1]
    name = base.split('--')[-1]

    final = name.split('/')[0]
    ext = name.split('.')[-1]

    final_ext = f"{final}.{ext}"

    shutil.copyfile(model_path, os.path.join(app_name, 'public', final_ext))

    del_base = base.split('snapshots/')[0]

    final_del_base = os.path.join(app_name, 'public', del_base)
    final_del_base_lock = os.path.join(app_name, 'public', '.locks')
    shutil.rmtree(final_del_base)
    shutil.rmtree(final_del_base_lock)

# models--TinyLlama--TinyLlama-1.1B-python-v0.1/snapshots/f8cb02e22e3da38ef962fe1eb1be7f70215253f7/ggml-model-q4_0.gguf
print("Model Downloaded")
# input("See")
