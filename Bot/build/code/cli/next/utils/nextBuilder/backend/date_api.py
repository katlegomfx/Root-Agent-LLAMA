# utils\nextBuilder\backend\date_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_api_route  # nopep8


def generate_latest_date_api():
    """Generate an API template that provides the latest date with separated components."""
    return f"""

export default async function handler(req, res) {{
    const {{ method }} = req;

    if (method === 'GET') {{
        const latestDate = new Date();
        
        // Formatting the date components
        const year = latestDate.getFullYear();
        const month = latestDate.getMonth() + 1;  // getMonth() is zero-based
        const day = latestDate.getDate();
        
        // Formatting the time components
        const hours = latestDate.getHours();
        const minutes = latestDate.getMinutes();
        const seconds = latestDate.getSeconds();

        // Creating a JSON response with the date and time components
        res.status(200).json({{
            year: year,
            month: month,
            day: day,
            time: `${{hours}}:${{minutes}}:${{seconds}}`
        }});
    }} else {{
        res.setHeader('Allow', ['GET']);
        res.status(405).end(`Method ${{method}} Not Allowed`);
    }}
}}
"""


def create_date_api_js_route():
    create_api_route('index', generate_latest_date_api().lstrip(), subdirectory="date")


if __name__ == "__main__":
    create_date_api_js_route()
