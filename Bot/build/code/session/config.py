import os

from Bot.build.code.session.constants import (
    ai_code_path,
    ai_errors_path,
    ai_results_path,
    ai_summaries_path,
    ai_history_path,
    gen_ai_path
)

build_paths = [
    ai_code_path,
    ai_errors_path,
    ai_results_path,
    ai_summaries_path,
    ai_history_path,
]

for path in build_paths:
    os.makedirs(os.path.join(gen_ai_path, path), exist_ok=True)
