# utils\nextBuilder\frontend\localFTP\ftp_ui_page.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8


def ftp_page():

    flex = """import FTPComponent from '@/components/FTPComponent'

export default function FTPPage() {

    return (
    <>
        <FTPComponent />
    </>
    );
}
"""
    return flex


create_page('page', ftp_page(), subdirectory='ftp')
