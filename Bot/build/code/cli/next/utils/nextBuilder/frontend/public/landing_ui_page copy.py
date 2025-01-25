# Bot\build\code\cli\next\utils\nextBuilder\frontend\public\landing_ui_page copy.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page, app_name, PAGE_DIR  # nopep8

def _page():

    flex = """
    import LandingComponent from '@/components/LandingComponent'
    import VideoView from '@/components/VideoView'

export default function AIPage() {

    return (
    <>
        <VideoView />
        <LandingComponent />
    </>
    );
}
"""

    return flex

def landing_page():

    flex = """import LandingComponent from '@/components/LandingComponent'

export default function AIPage() {

    return (
    <>
        <LandingComponent />
    </>
    );
}
"""

    return flex

def macho_page():

    flex = """import LandingComponent from '@/components/LandingComponent'

export default function AIPage() {

    return (
    <>
        <LandingComponent />
    </>
    );
}
"""

    return flex

path = os.path.join(app_name, PAGE_DIR, 'page.js')
if os.path.exists(path):
    os.remove(path)

if app_name.endswith('llm'):
    create_page('page', landing_page(), subdirectory='')

elif "macho" in app_name:
    create_page('page', macho_page(), subdirectory='')

else:
    create_page('page', landing_page(), subdirectory='')
