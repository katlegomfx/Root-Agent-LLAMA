# Bot\build\code\project_management\project.py
import os
import json
from Bot.build.code.llm.prompts import chat, extract_ordered_list_with_details, load_message_template, add_context_to_messages,
from Bot.build.code.session.constants import (
    code_prefix,
    assistant_prefix,
    summary_prefix,
    ai_code_path,
    ai_results_path,
    ai_history_path,
    ai_errors_path,
    ai_summaries_path,
    binary_answer,
    anonymised, error_file,
    triple_backticks,
    md_heading,
    gen_ai_path
)
from Bot.build.code.io_utils import get_next_filename_index, write_content_to_file
from Bot.build.code.llm.extract import extract_code

def load_project_data(path="task.json"):
    """Safely load JSON data from a file with error handling."""
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"No such file: {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}

def save_project_data(data, path="task.json"):
    """Save data to a JSON file with error handling."""
    print(f"Attempting to save data to {path}")
    try:
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {path}")
    except IOError as e:
        print(f"Failed to write to file: {path}, Error: {e}")
        raise

async def name_project(user_input, retries=0):

    name_project_convo = load_message_template(
        "python")
    project_name_prompt = f"""Considering the following project goal: {user_input}.
Name the project.
"""
    name_project_convo = add_context_to_messages(
        name_project_convo, 'name_project')
    name_project_convo.append(
        {'role': 'user', 'content': project_name_prompt}
    )
    result = await chat(name_project_convo)

    codes = extract_code(result)
    number_of_files = get_next_filename_index(ai_code_path, code_prefix)
    for code in codes:
        ### try to execute the python code if not retry        code_exec = exec(code)
        if code_exec != "":

            ### if execution worked            write_content_to_file(code, os.path.join(
                ai_code_path, f'{code_prefix}{number_of_files}.py'))
            projects = load_project_data()
            task_name = code_exec
            projects[task_name] = {"goal": user_input, "status": "Incomplete"}
            save_project_data(projects)

        else:
            if retries < (10/2):
                return name_project(user_input, retries=retries+1)
            else:
                ### input(colored('\nPlease try again?', 'red', attrs=[                ### "bold", "underline", "blink"]))                return name_project(user_input, retries=retries+1)

async def create_project_steps(project_name, project_goal, retries=0):
    projects = load_project_data()
    data_project = projects[project_name]

    steps_project_convo = load_message_template(
        "projectSteps")

    project_steps_prompt = f"""Working on {project_name}
Considering the following project: {data_project}.
Create a numbered list steps to complete the project goal: {project_goal}
"""

    steps_project_convo.append({
        'role': 'user', 'content': project_steps_prompt
    })
    response = await chat(steps_project_convo)

    correctness_prompt_messages = load_message_template(sys_type='base')
    correctness_prompt = f"""Given the following prompt:
{project_steps_prompt}
Given the following response:
{response}

Is the above list of steps sufficent?
{binary_answer}
"""
    correctness_prompt_messages.append({
        'role': 'user', 'content': correctness_prompt
    })
    correctness_response = await chat(correctness_prompt)

    if "yes" in correctness_response.lower():
        to_list_reponse = extract_ordered_list_with_details(response)
        data_project['steps'] = to_list_reponse
        projects[project_name] = data_project
        save_project_data(projects)
        return to_list_reponse
    else:
        if retries < (10/2):
            return create_project_steps(project_name, project_goal, retries=retries+1)
        else:
            ### input(colored('\nPlease try again?', 'red', attrs=[            ### "bold", "underline", "blink"]))            return create_project_steps(project_name, project_goal, retries=retries+1)

async def create_step_tasks(project_name, project_goal, project_step, retries=0):
    projects = load_project_data()
    data_project = projects[project_name]
    data_step = data_project['steps'][project_step]
    tasks_step_convo = load_message_template(
        "projectTasks")
    step_tasks_prompt = f"""The project goal is: {project_goal}
Considering the following project: {data_project}.
Create a numbered list tasks to complete the following project step: {data_step}
"""
    tasks_step_convo.append({
        'role': 'user', 'content': step_tasks_prompt
    })
    response = await chat(tasks_step_convo)

    correctness_prompt_messages = load_message_template(sys_type='base')
    correctness_prompt = f"""Given the following prompt:
{step_tasks_prompt}
Given the following response:
{response}

Is the above list of tasks sufficent?
{binary_answer}
"""
    correctness_prompt_messages.append({
        'role': 'user', 'content': correctness_prompt
    })
    correctness_response = await chat(correctness_prompt)
    if "yes" in correctness_response.lower():
        to_list_reponse = extract_ordered_list_with_details(response, "Task")
        data_step['tasks'] = to_list_reponse
        projects[project_name]['steps'][project_step] = data_step
        save_project_data(projects)
        return to_list_reponse
    else:
        if retries < (10/2):
            return create_step_tasks(project_name, project_goal, project_step, retries=retries+1)
        else:
            ### input(colored('\nPlease try again?', 'red', attrs=[            ### "bold", "underline", "blink"]))            return create_step_tasks(project_name, project_goal, project_step, retries=retries+1)

async def create_task_process(project_name, project_goal, project_step, project_task, retries=0):
    projects = load_project_data()
    data_project = projects[project_name]
    data_step = data_project['steps'][project_step]
    data_task = data_step['tasks'][project_task]
    task_process_prompt = f"""The project goal is: {project_goal}
Look at the following project step: {data_step}.
Considering the following project: {data_project}.
Describe actions in python code or shell code to complete the following project task: {data_task}.
"""
    process_task_convo = load_message_template("projectProcess")

    process_task_convo.append({
        'role': 'user', 'content': task_process_prompt
    })

    process_response = await chat(process_task_convo)

    if process_response[1] in ["python", "sh", "json tool"]:
        if process_response[0]['result'][0][0] == True:
            run_response = process_response[0]['result'][0][1]
            data_task['processing'] = run_response
            projects[project_name]['steps'][project_step]["tasks"][project_task] = data_task
            save_project_data(projects)
            return run_response
        else:
            if retries < (10/2):
                return create_task_process(project_name, project_goal,
                                           project_step, project_task, retries=retries+1)
            else:
                ### input(colored('\nPlease try again?', 'red', attrs=[                ###     "bold", "underline", "blink"]))                return create_task_process(project_name, project_goal,
                                           project_step, project_task, retries=retries+1)

    elif process_response[1] == "text":
        run_response = process_response[0]
        data_task['processing'] = run_response
        projects[project_name]['steps'][project_step]["tasks"][project_task] = data_task
        save_project_data(projects)
        return run_response
    else:
        if retries < (10/2):
            return create_task_process(project_name, project_goal,
                                       project_step, project_task, retries=retries+1)
        else:
            ### input(colored('\nPlease try again?', 'red', attrs=[            ### "bold", "underline", "blink"]))            return create_task_process(project_name, project_goal,
                                       project_step, project_task, retries=retries+1)

def doLive(goal):
    base_projects = load_project_data()
    incomplete_task = [key for key, value in base_projects.items()
                       if value["status"] == "Incomplete"]
    if len(incomplete_task) >= 1:
        project_name = incomplete_task[0]
    else:
        project_name = name_project(goal)
    if 'steps' not in load_project_data()[project_name]:
        base_steps = create_project_steps(project_name, goal)
    for step in load_project_data()[project_name]['steps']:
        base_tasks = create_step_tasks(project_name, goal, step)
        for task in load_project_data()[project_name]['steps'][step]['tasks']:
            base_process = create_task_process(project_name, goal, step, task)
