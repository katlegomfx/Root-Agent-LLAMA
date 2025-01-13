# utils\shared.py

from string import Template
import os
import re
import json

# Constants for directory paths
STORE_DIR = "src/store"
API_AUTH_DIR = "src/pages/api/auth"
COMPONENT_DIR = "src/components"
MIGRATIONS_DIR = "src/migrations"
PAGE_DIR = "src/app"
API_ROUTE_DIR = "src/pages/api"
MIDDLEWARE_ROUTE_DIR = "src/middleware"
UTILS_DIR = "src/lib/utils"

venv_name = 'pyllms'
app_name = "next-macho"
db_name = "flex_development"

node_path = "\"C:\\Program Files\\nodejs\\node.exe\""
npm_path = "\"C:\\Program Files\\nodejs\\npm.cmd\""
npx_path = "\"C:\\Program Files\\nodejs\\npx.cmd\""

config = {
    'component_dir': COMPONENT_DIR,
    'page_dir': PAGE_DIR,
    'api_route_dir': API_ROUTE_DIR,
    'app_name': app_name,
    # Add more configuration as needed
}

def ensure_folder_exists(folder_path):
    """Ensure that a folder exists, creating it if necessary."""
    os.makedirs(folder_path, exist_ok=True)


def create_file_in_directory(directory, name, content, extension='jsx'):
    """Generalized function to create a file with the specified content in a given directory."""
    file_path = os.path.join(app_name, directory, f'{name}.{extension}')
    write_to_file(file_path, content)


def create_component(name, content, extension='jsx'):
    """Create a React component file in JavaScript."""
    file_path = os.path.join(app_name, COMPONENT_DIR, f'{name}.{extension}')
    write_to_file(file_path, content)


def create_page(name, content, subdirectory=""):
    """Create a Next.js page file, optionally within a subdirectory."""
    directory = PAGE_DIR if subdirectory == "" else os.path.join(
        PAGE_DIR, subdirectory)
    create_file_in_directory(directory, name, content)


def create_middleware_route(name, content, subdirectory=""):
    """Create a Next.js API route file, optionally within a subdirectory."""
    directory = MIDDLEWARE_ROUTE_DIR if subdirectory == "" else os.path.join(
        API_ROUTE_DIR, subdirectory)
    create_file_in_directory(directory, name, content, extension='js')

def create_api_route(name, content, subdirectory=""):
    """Create a Next.js API route file, optionally within a subdirectory."""
    directory = API_ROUTE_DIR if subdirectory == "" else os.path.join(
        API_ROUTE_DIR, subdirectory)
    create_file_in_directory(directory, name, content, extension='js')


def render_template(template_path, context={}):
    """Render a template with given context."""
    template_content = load_template(template_path)
    return Template(template_content).substitute(context)


def load_template(template_path):
    """Load a template file's content."""
    full_path = os.path.join(app_name, 'src', template_path)
    with open(full_path, 'r', encoding='utf-8') as file:
        return file.read()


def extract_table_details_from_migration(migration_filename):
    """
    Extract table name and fields with their types from the migration file.
    """
    with open(migration_filename, 'r') as file:
        migration_content = file.read()

    # Extract table name
    table_name = re.findall(
        r"await queryInterface\.createTable\('(\w+)'", migration_content)[0]

    # Extract fields and their types
    field_blocks = re.findall(
        r"(\w+): {\s*type: Sequelize\.(\w+)", migration_content)
    fields = {field: data_type for field, data_type in field_blocks}

    # Extract primary key field
    primary_key_match = re.findall(
        r"(\w+): {\s*type: Sequelize\.\w+,\s*allowNull: \w+,\s*primaryKey: true", migration_content)
    primary_key = primary_key_match[0] if primary_key_match else None

    fields['primary_key'] = primary_key

    return table_name, fields


def create_redux_store_js(template):
    store_dir_path = os.path.join(app_name, 'src', 'store')
    store_file_path = os.path.join(store_dir_path, 'index.js')
    write_to_file(store_file_path, template)


def create_redux_reducer_js(template, item):
    store_dir_path = os.path.join(app_name, 'src', 'store', 'states')
    store_file_path = os.path.join(store_dir_path, f'{item}.js')
    write_to_file(store_file_path, template)


def generate_specific_api_template(model_name, fields):
    """Generate the API template for specific model item operations."""

    primary_key = fields.get('primary_key')
    return f"""// JavaScript content for specific operations on {model_name} with ID {primary_key}
import db from '../../../models';

export default async function handler(req, res) {{
    const {{ query: {{ {primary_key} }}, method, body }} = req;
    switch (method) {{
        case 'GET':
            // Fetch a single {model_name} by {primary_key}
            break;
        case 'PUT':
            // Update a {model_name} by {primary_key}
            break;
        case 'DELETE':
            // Delete a {model_name} by {primary_key}
            break;
        default:
            res.setHeader('Allow', ['GET', 'PUT', 'DELETE']);
            res.status(405).end(`Method ${{method}} Not Allowed`);
    }}
}}
""".strip()

def extract_table_details_from_migration(migration_filename):
    """
    Extract table name and fields with their types from the migration file.
    """
    with open(migration_filename, 'r') as file:
        migration_content = file.read()

    # Extract table name
    table_name = re.findall(
        r"await queryInterface\.createTable\('(\w+)'", migration_content)[0]

    # Extract fields and their types
    field_blocks = re.findall(
        r"(\w+): {\s*type: Sequelize\.(\w+)", migration_content)
    fields = {field: data_type for field, data_type in field_blocks}

    # Extract primary key field
    primary_key_match = re.findall(
        r"(\w+): {\s*type: Sequelize\.\w+,\s*allowNull: \w+,\s*primaryKey: true", migration_content)
    primary_key = primary_key_match[0] if primary_key_match else None

    fields['primary_key'] = primary_key

    return table_name, fields


def get_input_type(data_type):
    # Map your Sequelize data types to input types (you might need to expand this)
    return {
        "STRING": "text",
        "INTEGER": "number",
        "BOOLEAN": "checkbox",
        # Add more mappings as needed
    }.get(data_type, "text")


def generate_state_update_code(field_name):
    """
    Generate the code for updating the state for a specific field.
    This replaces the use of the spread operator from the JavaScript syntax.
    """
    return "{...formState, '" + field_name + "': e.target.value }"


def read_json_manifest(file_path):
    """Read and return the content of a JSON manifest file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def filter_entities_by_role(manifest, role_key):
    """Filter and return entities based on a specific role access key."""
    return [entity for entity, attributes in manifest.items() if attributes.get(role_key) == 'yes']


def create_link_element(model_name, role):
    """Create and return a link element for the React component."""
    url_path = f"/{role}/{model_name}"
    model_name_cap = model_name.capitalize()
    link = (
        f'''<li className="mb-4 mr-4">
    <Link href="{url_path}">
        <div className="text-black hover:text-gray-800 border border-gray-300 rounded px-4 py-2 inline-flex items-center">{model_name_cap} View <span className="ml-2">&#x2192;</span></div>
    </Link>
</li>'''
    )
    return link


def generate_main_component_content_without(links, role):
    role_cap = role.capitalize()
    role_low = role.lower()

    return f"""'use client'
import React from 'react';
import {{ useDispatch }} from 'react-redux';
import {{ setActiveComponent, setActiveItem }} from '@/store/states/uiSlice';
import Link from 'next/link';

export default function {role_cap}MainLinks() {{
    const dispatch = useDispatch();

    return (
        <main className="pt-20 flex min-h-screen flex-col items-center justify-start p-10 bg-gray-100">
            <div className="w-full mb-6">
                <ul className="flex flex-wrap justify-center">
                    {links}
                </ul>
            </div>
        </main>
    );
}}
"""


def generate_main_component_content_with_state(links, role):
    role_cap = role.capitalize()
    role_low = role.lower()

    return f"""'use client'
import React from 'react';
import {{ useDispatch }} from 'react-redux';
import {{ setActiveComponent, setActiveItem }} from '@/store/states/uiSlice';
import Link from 'next/link';
import useRedirectIfUnauthenticated from "@/components/deauthedWrapper";

export default function {role_cap}MainLinks() {{
    useRedirectIfUnauthenticated();
    const dispatch = useDispatch();

    return (
        <main className="pt-20 flex min-h-screen flex-col items-center justify-start p-10 bg-gray-100">
            <div className="w-full mb-6">
                <ul className="flex flex-wrap justify-center">
                    {links}
                </ul>
            </div>
        </main>
    );
}}
"""


def generate_main_component_content(links, role):
    """Generate the main page content for a React component based on the role."""
    template = """'use client'
    import React from 'react';
    import Link from 'next/link';
    import useRedirectIfUnauthenticated from "@/components/deauthedWrapper";

    export default function {role}MainLinks() {{
      useRedirectIfUnauthenticated()
      return (
        <>
          <ul className="flex flex-wrap justify-center">
            {links}
          </ul>
        </>
      );
    }}
    """
    return template.format(role=role.capitalize(), links="\n".join(links))


def write_to_file(file_path, content):
    """Write given content to a specified file path."""
    ensure_folder_exists(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def process_migration_files(migrations_dir, entities, role):
    """Process migration files and return a list of links based on the role."""
    links = []
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, _ = extract_table_details_from_migration(
                migration_filename)
            if entities != None and table_name in entities:
                links.append(create_link_element(table_name, role))
            if entities == None:
                links.append(create_link_element(table_name, role))
    return links


def generate_grid_items(fields, model_name):
    primary_key = fields['primary_key']
    item_content = '\n'.join(
        f'<div className="text-black">{field}: {{record.{field}}}</div>' for field in fields if field not in [primary_key, 'primary_key']
    )
    update_delete_buttons = f"""
        <div className="flex justify-around mt-2">
            <button onClick={{() => handleEdit(record.{primary_key})}} className="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded">Update</button>
            <button onClick={{() => handleDelete(record.{primary_key})}} className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded">Delete</button>
        </div>
    """
    return f"""
    {{records.map((record, index) => (
        <div key={{index}} className="bg-white p-6 rounded-lg shadow-md">
            {item_content + update_delete_buttons}
        </div>
    ))}}
    """

def generate_grid_items_without(fields, model_name):
    primary_key = fields['primary_key']
    item_content = '\n'.join(
        f'<div className="text-black">{field}: {{record.{field}}}</div>' for field in fields if field not in [primary_key, 'primary_key']
    )
    update_delete_buttons = f"""
        <div className="flex justify-around mt-2">
            <button onClick={{() => handleEdit(record.{primary_key})}} className="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded">Update</button>
            <button onClick={{() => handleDelete(record.{primary_key})}} className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded">Delete</button>
        </div>
    """
    return f"""
    {{records.map((record, index) => (
        <div key={{index}} className="bg-white p-6 rounded-lg shadow-md">
            {item_content}
        </div>
    ))}}
    """


def create_react_page_template_without(model_name, role, grid_items, fields):
    primary_key = fields['primary_key']
    model_name_cap = model_name.capitalize()
    model_name_low = model_name.lower()
    grid_payload = grid_items
    return f"""'use client'
import Link from 'next/link';
import React, {{ useState, useEffect }} from 'react';
import {{ useRouter }} from 'next/navigation';
import {{ useDispatch }} from 'react-redux';
import {{ setActiveComponent, setActiveItem }} from '@/store/states/uiSlice'; // Adjust the path as needed

export default function {model_name_cap}{role}Content() {{
    const router = useRouter();
    const dispatch = useDispatch();
    const [records, setRecords] = useState([]);
    const [action, setAction] = useState(false);

    useEffect(() => {{
        async function fetchRecords() {{
            const response = await fetch('/api/{model_name}');
            const data = await response.json();
            setRecords(data || []);
            setAction(false)
        }}
        fetchRecords();
    }}, [action]);

    const handleCreateNew = () => {{
        dispatch(setActiveItem(null)); // For creating a new item
        dispatch(setActiveComponent('create'));
    }};

    const handleEdit = (id) => {{
        // Find the record with the matching id
        const recordToEdit = records.find(record => record.{primary_key} === id);
        dispatch(setActiveItem(recordToEdit));
        dispatch(setActiveComponent('update'));
    }};

    const handleDelete = async (id) => {{
        if (window.confirm('Are you sure you want to delete this {model_name_low}?')) {{
            await fetch(`/api/{model_name_low}/${{id}}`, {{ method: 'DELETE' }});
            setAction(true)
            setRecords(records.filter(record => record.id !== id));
        }}
    }};

    return (
        <main className="pt-20 flex min-h-screen flex-col items-center justify-start p-10 bg-gray-100">
            <div className="w-full mb-6">
                <h1 className="text-2xl font-bold text-gray-800">{model_name_cap} {role} Page</h1>
            </div>
            <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-4">
                {grid_payload}
            </div>
        </main>
    );
}}
"""


def create_react_page_template(model_name, role, grid_items, fields):
    primary_key = fields['primary_key']
    model_name_cap = model_name.capitalize()
    model_name_low = model_name.lower()
    # grid_payload = f"""{grid_items.format(handle_edit='handleEdit',handle_delete='handleDelete')}"""
    grid_payload = grid_items
    # Assuming 'setActiveComponent' and 'setActiveItem' are actions defined in your uiSlice for Redux.
    return f"""'use client'
import Link from 'next/link';
import React, {{ useState, useEffect }} from 'react';
import {{ useRouter }} from 'next/navigation';
import {{ useDispatch }} from 'react-redux';
import {{ setActiveComponent, setActiveItem }} from '@/store/states/uiSlice'; // Adjust the path as needed
import useRedirectIfUnauthenticated from "@/components/deauthedWrapper";

export default function {model_name_cap}{role}Content() {{
    useRedirectIfUnauthenticated();
    const router = useRouter();
    const dispatch = useDispatch();
    const [records, setRecords] = useState([]);
    const [action, setAction] = useState(false);

    useEffect(() => {{
        async function fetchRecords() {{
            const response = await fetch('/api/{model_name}');
            const data = await response.json();
            setRecords(data || []);
            setAction(false)
        }}
        fetchRecords();
    }}, [action]);

    const handleCreateNew = () => {{
        dispatch(setActiveItem(null)); // For creating a new item
        dispatch(setActiveComponent('create'));
    }};

    const handleEdit = (id) => {{
        // Find the record with the matching id
        const recordToEdit = records.find(record => record.{primary_key} === id);
        dispatch(setActiveItem(recordToEdit));
        dispatch(setActiveComponent('update'));
    }};

    const handleDelete = async (id) => {{
        if (window.confirm('Are you sure you want to delete this {model_name_low}?')) {{
            await fetch(`/api/{model_name_low}/${{id}}`, {{ method: 'DELETE' }});
            setAction(true)
            setRecords(records.filter(record => record.id !== id));
        }}
    }};

    return (
        <main className="pt-20 flex min-h-screen flex-col items-center justify-start p-10 bg-gray-100">
            <div className="w-full mb-6">
                <h1 className="text-2xl font-bold text-gray-800">{model_name_cap} {role} Page</h1>
                <button 
                    onClick={{handleCreateNew}}
                    className="mt-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    Create New {model_name_cap}
                </button>
            </div>
            <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-4">
                {grid_payload}
            </div>
        </main>
    );
}}
"""


def create_component_file_for_entity(entity, fields, role, directory):
    grid_items = generate_grid_items(fields, entity)
    page_content = create_react_page_template(entity, role, grid_items)
    file_path = os.path.join(directory, f"{entity.capitalize()}Component.jsx")
    write_to_file(file_path, page_content)


def create_form_template(entity, entity_cap, fields, primary_key, role):
    entity_low = entity.lower()
    form_fields = "\n".join([
        f"""<div className="mb-4">
            <label htmlFor="{field_name}" className="block text-gray-700 text-sm font-bold mb-2">{field_name.capitalize()}</label>
            <input 
                id="{field_name}" 
                type="{get_input_type(fields[field_name])}" 
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                value={{formState['{field_name}']}} 
                onChange={{e => setFormState({{...formState, '{field_name}': e.target.value}})}} 
            />
        </div>"""
        for field_name in fields if field_name not in ['primary_key', primary_key]
    ])

    handleSubmit_function = f"""
    const handleSubmit = async (e) => {{
        e.preventDefault();
        const apiUrl = activeItem ? `/api/{entity_low}/${{activeItem.{primary_key}}}` : '/api/{entity_low}';
        const method = activeItem ? 'PUT' : 'POST';

        try {{
            const response = await fetch(apiUrl, {{
                method: method,
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(formState),
            }});
            if (response.ok) {{
                dispatch(setActiveComponent('list'))
                alert('{entity_cap} ' + (activeItem ? 'updated' : 'created') + ' successfully');
            }} else {{
                alert('Error: ' + await response.text());
                
            }}
        }} catch (error) {{
            console.error(error);
            alert('An error occurred, please try again.');
        }}
    }};
    """

    component_template = f"""'use client'
import React, {{ useState, useEffect }} from 'react';
import {{ useDispatch, useSelector }} from 'react-redux';
import {{ setActiveComponent, setActiveItem, selectActiveItem }} from '@/store/states/uiSlice';

export default function {entity_cap}{role}Form() {{
    const dispatch = useDispatch();
    const activeItem = useSelector(selectActiveItem);
    const [formState, setFormState] = useState({{{', '.join(f"'{field}': ''" for field in fields if field != primary_key)}}});

    useEffect(() => {{
        if (activeItem) {{
            setFormState({{
                ...formState,
                ...activeItem
            }});
        }}
    }}, [activeItem]); 

    {handleSubmit_function}

    return (
        <div className="flex items-center justify-center h-screen">
            <div className="w-full max-w-xs">
                <form onSubmit={{handleSubmit}} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                    {form_fields}
                    <div className="flex items-center justify-between">
                        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                            {{activeItem ? 'Update' : 'Create'}}
                        </button>
                        <button onClick={{() => dispatch(setActiveComponent('list'))}} className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800" type="button">
                            Go Back
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}}
"""
    return component_template


def create_form_for_entity(entity, fields, primary_key, role, directory):
    entity_cap = entity.capitalize()
    entity_low = entity.lower()
    form_content = create_form_template(
        entity, entity_cap, fields, primary_key, role)

    if role == 'Public':
        entity_dir_path = os.path.join(directory, 'home', entity)
    else:
        entity_dir_path = os.path.join(directory, role, entity)

    form_path = os.path.join(
        entity_dir_path, f"{entity_cap}{role}Form.jsx")

    write_to_file(form_path, form_content)


def generate_components_for_role(migrations_dir, role, directory, manifest=None):
    entities = read_json_manifest(manifest) if manifest else None
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)
            if not entities or table_name in entities:
                create_component_file_for_entity(
                    table_name, fields, role, directory)


def create_view_component(model_name, model_name_cap, model_name_low, fields, role):

    if role == "Public":
        role_lower = "home"
    else:
        role_lower = role.lower()


    flex = f"""'use client'
import {model_name_cap}{role}Content from '@/components/{role_lower}/{model_name}/{model_name_cap}{role}Content'
import {model_name_cap}{role}Form from '@/components/{role_lower}/{model_name}/{model_name_cap}{role}Form'
import {{ useSelector, useDispatch }} from 'react-redux';
import {{ selectUIState }} from '@/store/states/uiSlice';

export default function {model_name_cap}{role}Component() {{
    const dispatch = useDispatch();
    const {{ activeComponent, activeItem }} = useSelector(selectUIState);

    const componentMapping = {{
        'none': {model_name_cap}{role}Content, 
        'create': {model_name_cap}{role}Form,
        'update': {model_name_cap}{role}Form, 
    }};

    // Select the component based on the activeComponent state
    const ActiveComponent = componentMapping[activeComponent] || componentMapping['none'];

    return (
    <div>
            <ActiveComponent activeUIItem={{activeItem}} />
        </div>
    );
}}
"""

    return flex
