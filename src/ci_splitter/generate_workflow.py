import os
import yaml

def generate_github_actions_workflow(test_files, num_jobs=4):
    test_distribution = distribute_tests(test_files, num_jobs)
    
    workflow = {
        'name': 'Parallel Tests',
        'on': ['push', 'pull_request'],
        'jobs': {}
    }
    
    for job_num in range(num_jobs):
        job_name = f'test-group-{job_num + 1}'
        workflow['jobs'][job_name] = {
            'runs-on': 'ubuntu-latest',
            'steps': [
                {'uses': 'actions/checkout@v3'},
                
                {
                    'name': 'Set up Python',
                    'uses': 'actions/setup-python@v3',
                    'with': {'python-version': '3.9'}
                },
                
                {
                    'name': 'Install Poetry',
                    'uses': 'snok/install-poetry@v1',
                    'with': {
                        'virtualenvs-create': True,
                        'virtualenvs-in-project': True
                    }
                },
                
                {
                    'name': 'Load cached venv',
                    'id': 'cached-poetry-dependencies',
                    'uses': 'actions/cache@v3',
                    'with': {
                        'path': '.venv',
                        'key': f'venv-{{"runner.os"}}-{{"steps.setup-python.outputs.python-version"}}-{{"hashFiles("**/poetry.lock")}}'
                    }
                },
                
                {
                    'name': 'Install dependencies',
                    'if': 'steps.cached-poetry-dependencies.outputs.cache-hit != "true"',
                    'run': 'poetry install --no-interaction --no-root'
                },
                
                {
                    'name': 'Install project',
                    'run': 'poetry install --no-interaction'
                },
                
                {
                    'name': f'Run tests for job {job_num + 1}',
                    'run': f'poetry run pytest {" ".join(test_distribution[job_num])}'
                }
            ]
        }
    
    return workflow

def distribute_tests(test_files, num_jobs):
    sorted_tests = sorted(test_files)
    
    job_tests = [[] for _ in range(num_jobs)]
    for i, test_file in enumerate(sorted_tests):
        job_tests[i % num_jobs].append(test_file)
    
    return job_tests

def write_workflow_file(workflow):
    os.makedirs('.github/workflows', exist_ok=True)
    
    workflow_path = '.github/workflows/parallel_tests.yml'
    with open(workflow_path, 'w') as f:
        yaml.dump(workflow, f, default_flow_style=False)
    
    print(f'Workflow file generated: {workflow_path}')

if __name__ == '__main__':
    test_files = [
        'tests/test_math_1.py',
        'tests/test_math_2.py',
        'tests/test_math_3.py',
        'tests/test_math_4.py',
        'tests/test_math_5.py',
        'tests/test_math_6.py',
        'tests/test_math_7.py',
        'tests/test_math_8.py',
    ]
    
    workflow = generate_github_actions_workflow(test_files, num_jobs=4)
    
    write_workflow_file(workflow)