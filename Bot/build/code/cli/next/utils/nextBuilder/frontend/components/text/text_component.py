# utils\nextBuilder\frontend\components\text\text_component.py
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    write_to_file,
    COMPONENT_DIR,
    app_name
)


def create_view_component_2(model_name, model_name_cap):

    flex = f"""'use client'
import {model_name_cap}Content from '@/components/{model_name_cap}Content'
import {model_name_cap}CommentForm from '@/components/{model_name_cap}CommentForm'
import {model_name_cap}Viewer from '@/components/{model_name_cap}Viewer'
import {{ useSelector, useDispatch }} from 'react-redux';
import {{ selectUIState }} from '@/store/states/uiSlice';

export default function {model_name_cap}Component({{ setting }}) {{
    const dispatch = useDispatch();
    const {{ activeComponent, activeItem }} = useSelector(selectUIState);

    const componentMapping = {{
        'none': {model_name_cap}Content, 
        'create': {model_name_cap}CommentForm,
        'view': {model_name_cap}Viewer, 
    }};
    if (setting === 'landing') {{
        const componentMapping = {{
            'none': {model_name_cap}Viewer, 
            'create': {model_name_cap}CommentForm,
            'view': {model_name_cap}Content, 
        }};
    }}
    
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



def create_components():

    component_content = create_view_component_2(
        'text', 'Text')

    # Define the component directory path
    model_dir = os.path.join(app_name,
                                    COMPONENT_DIR,)

    # Path where the component will be saved
    component_path = os.path.join(
        model_dir, f"TextComponent.jsx")

    write_to_file(
        component_path, component_content)


if __name__ == "__main__":
    create_components()
