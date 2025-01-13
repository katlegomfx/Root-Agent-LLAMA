# utils\api\nextdb.py
import sys
import subprocess
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_db():
    commands = [
        f'{sys.executable} utils/nextBuilder/database/setupDB.py',
        f'{sys.executable} utils/nextBuilder/database/database_rollback.py',
        f'{sys.executable} utils/nextBuilder/database/sequelize_model_creator.py',
        f'{sys.executable} utils/nextBuilder/database/model_index.py',
        f'{sys.executable} utils/nextBuilder/database/database_migration.py',
        f'{sys.executable} utils/nextBuilder/database/sequelize_seeder.py',

        f'{sys.executable} utils/nextBuilder/database/seeder_data_creator.py',

        f'{sys.executable} utils/nextBuilder/database/database_user_seeding.py',
        
        f'{sys.executable} utils/nextBuilder/database/data.py',
        
        f'{sys.executable} utils/nextBuilder/database/database_seeding.py',
    ]
    
    for command in commands:
        print(f"Executing: {command}")
        process = subprocess.Popen(command, shell=True)
        process.wait()  # Wait for the command to complete


    logging.info("Finished DB Build")

if __name__ == "__main__":
    create_db()