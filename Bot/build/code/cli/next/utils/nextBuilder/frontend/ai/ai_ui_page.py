# utils\nextBuilder\frontend\ai\ai_ui_page.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8


def ai_page():

    flex = """import AIComponent from '@/components/AIComponent'

export default function AIPage() {

    return (
    <>
        <AIComponent />
    </>
    );
}
"""

    return flex

create_page('page', ai_page(), subdirectory='llm')
