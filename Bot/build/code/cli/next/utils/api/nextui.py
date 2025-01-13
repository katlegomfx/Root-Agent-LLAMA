# utils\api\nextui.py
import subprocess
import sys
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_uis():
    commands = [

        # Public
        f'{sys.executable} utils/nextBuilder/frontend/public/landing_ui_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/public/components/landing_ui_component.py',

        # Gneeral Components
        # f'{sys.executable} utils/nextBuilder/frontend/components/videoView.py',
        # f'{sys.executable} utils/nextBuilder/frontend/components/videoList.py',
        # f'{sys.executable} utils/nextBuilder/frontend/components/musicView.py',
        # f'{sys.executable} utils/nextBuilder/frontend/components/musicList.py',
        # f'{sys.executable} utils/nextBuilder/frontend/components/articleView.py',
        # f'{sys.executable} utils/nextBuilder/frontend/components/articleList.py',
        
        f'{sys.executable} utils/nextBuilder/frontend/components/socialLinks.py',

        # Text
        f'{sys.executable} utils/nextBuilder/frontend/components/text/text_interactive_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/text/text_viewer_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/text/text_content_component.py',        
        f'{sys.executable} utils/nextBuilder/frontend/components/text/text_component.py',

        # Video
        f'{sys.executable} utils/nextBuilder/frontend/components/video/video_interactive_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/video/video_player_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/video/video_content_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/video/video_component.py',

        # Music
        f'{sys.executable} utils/nextBuilder/frontend/components/music/music_interactive_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/music/music_player_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/music/music_content_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/components/music/music_component.py',


        # Store feature
        f'{sys.executable} utils/nextBuilder/frontend/store/cart_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/store/components/cart_component.py',

        f'{sys.executable} utils/nextBuilder/frontend/store/checkout_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/store/components/checkout_component.py',

        f'{sys.executable} utils/nextBuilder/frontend/store/order_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/store/components/order_component.py',

        f'{sys.executable} utils/nextBuilder/frontend/store/productList_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/store/components/productList_component.py',

        f'{sys.executable} utils/nextBuilder/frontend/store/productListWildcard_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/store/components/productView_component.py',


        # f'{sys.executable} utils/nextBuilder/frontend/store/components/search_component.py',



        # Basic
        f'{sys.executable} utils/nextBuilder/frontend/basic/layout.py',
        f'{sys.executable} utils/nextBuilder/frontend/basic/components/backButton.py',
        
        f'{sys.executable} utils/nextBuilder/frontend/basic/components/navCart.py',
        f'{sys.executable} utils/nextBuilder/frontend/basic/components/backButton.py',
        f'{sys.executable} utils/nextBuilder/frontend/basic/components/footer.py',
        f'{sys.executable} utils/nextBuilder/frontend/basic/components/navbar.py',

        # Auth
        f'{sys.executable} utils/nextBuilder/frontend/auth/login_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/components/loginForm_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/register_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/components/registerForm_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/reset_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/components/resetForm_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/send_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/components/sendForm_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/wait_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/components/waitForm_component.py',

        f'{sys.executable} utils/nextBuilder/frontend/auth/components/authed_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/auth/components/deauth_component.py',

        # # Core AI chatbot UI
        # f'{sys.executable} utils/nextBuilder/frontend/ai/ai_ui_page.py',
        # f'{sys.executable} utils/nextBuilder/frontend/ai/components/ai_ui_component.py',

        # #  Builder UI
        # f'{sys.executable} utils/nextBuilder/frontend/localFTP/ftp_ui_page.py',
        # f'{sys.executable} utils/nextBuilder/frontend/localFTP/components/ftp_ui_component.py',



        #  Home UI
        f'{sys.executable} utils/nextBuilder/frontend/home/home_main_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/home/home_content_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/home/components/home_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/home/components/home_content_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/home/components/home_main_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/home/components/home_interactive_component.py',


        #  Creator UI
        f'{sys.executable} utils/nextBuilder/frontend/creator/creator_main_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/creator/creator_content_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/creator/components/creator_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/creator/components/creator_content_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/creator/components/creator_main_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/creator/components/creator_interactive_component.py',


        #  Admin UI
        f'{sys.executable} utils/nextBuilder/frontend/admin/admin_main_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/admin/admin_content_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/admin/components/admin_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/admin/components/admin_content_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/admin/components/admin_main_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/admin/components/admin_interactive_component.py',

        #  User UI
        f'{sys.executable} utils/nextBuilder/frontend/user/user_main_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/user/user_content_page.py',
        f'{sys.executable} utils/nextBuilder/frontend/user/components/user_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/user/components/user_content_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/user/components/user_main_component.py',
        f'{sys.executable} utils/nextBuilder/frontend/user/components/user_interactive_component.py',

    ]
    
    for command in commands:
        print(f"Executing: {command}")
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Wait for the command to complete


    logging.info("Finished UI Build")

if __name__ == "__main__":
    create_uis()