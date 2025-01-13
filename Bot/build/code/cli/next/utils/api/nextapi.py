# utils\api\nextapi.py
import subprocess
import sys
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_apis():
    commands = [
        # Api
        f'{sys.executable} utils/nextBuilder/backend/ai/ai_api.py',

        # Email
        f'{sys.executable} utils/nextBuilder/backend/smpt_api.py',

        # Middleware
        f'{sys.executable} utils/nextBuilder/backend/authMiddleware.py',
        f'{sys.executable} utils/nextBuilder/backend/middleware.py',

        # Redux site
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_state_api.py',
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_ui_api.py',
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_siteInfo_api.py',
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_geo_api.py',
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_past_api.py',

        # Redux component
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_cart_api.py',
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_delivery_api.py',
        f'{sys.executable} utils/nextBuilder/backend/redux/redux_nft_api.py',

        # Application
        f'{sys.executable} utils/nextBuilder/backend/session_api.py',
        f'{sys.executable} utils/nextBuilder/backend/click_api.py',
        f'{sys.executable} utils/nextBuilder/backend/geo_api.py',
        f'{sys.executable} utils/nextBuilder/backend/siteInfo_api.py',
        f'{sys.executable} utils/nextBuilder/backend/date_api.py',

        # Auth
        f'{sys.executable} utils/nextBuilder/backend/auth_route_api.py',
        f'{sys.executable} utils/nextBuilder/backend/login_api.py',
        f'{sys.executable} utils/nextBuilder/backend/register_api.py',

        # Database
        f'{sys.executable} utils/nextBuilder/backend/model_api.py',
        f'{sys.executable} utils/nextBuilder/backend/model_wildcard_api.py',
        
        # Utils
        f'{sys.executable} utils/nextBuilder/backend/utils_api.py',
        f'{sys.executable} utils/nextBuilder/backend/date_utils_api.py',

    ]
    
    for command in commands:
        logging.info(f"Executing: {command}")
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Wait for the command to complete
        # logging.info(f"Succesfully executed: {command}")


    logging.info("Finished API Build")

if __name__ == "__main__":
    create_apis()
