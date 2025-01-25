# Bot\build\code\cli\next\utils\nextBuilder\database\model_index.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import  write_to_file, MIGRATIONS_DIR, app_name  # nopep8

def generate_api_template(models):
    """Generate the API template for given migrations."""

    imports = [f"import {model}Model from './{model}'\n" for model in models]
    db = [
        f"const {model[0].capitalize()}{model[1:]} = {model}Model(sequelize, Sequelize.DataTypes);\n" for model in models]
    variables = [f"{model[0].capitalize()}{model[1:]},\n" for model in models]

    return f"""
// src\models\index.js
const Sequelize = require('sequelize');
const config = require('@/config/config.json');
// const config = require('../src/config/config.json'); // Adjust the path based on where your config.js is located

{''.join(imports)}

// Choose the environment. For this example, I'm using 'development'.
// In a real-world scenario, you might use something like process environment NODE_ENV to determine the environment.
const env = 'development';
const dbConfig = config[env];

const sequelize = new Sequelize(dbConfig.database, dbConfig.username, dbConfig.password, {{
  host: dbConfig.host,
  dialect: dbConfig.dialect,
  logging: dbConfig.logging,
}});

{''.join(db)}

const db = {{
  sequelize,
  Sequelize,

  {''.join(variables)}
}};

module.exports = db;

sequelize.sync()
  .then(() => {{
    console.log('Database & tables created or updated!');
  }})
  .catch(error => {{
    console.error('Error syncing database:', error);
  }});

"""

def create_model_index():
    """Create an API route for the given model."""
    new_path_api_dir = os.path.join(app_name, 'src/models', )
    path = os.path.join(new_path_api_dir, f"index.js")
    write_to_file(path, generate_api_template(models()).lstrip())

def models():
    """Main function to generate API routes for each migration file."""
    return [f'{migration_file.split("-")[1].split("_")[0]}' for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)) if migration_file.endswith(".js")]

create_model_index()
