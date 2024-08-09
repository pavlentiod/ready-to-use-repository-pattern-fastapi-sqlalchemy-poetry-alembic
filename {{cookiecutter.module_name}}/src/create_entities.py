import os

# Directories to be created
directories = [
    'repositories',
    'services',
    'routers',
    'schemas',
    'tests',
    'database/models'
]

# Template files content
# with open('templates/repository.txt','r') as f:
#     repository_template = f.read()
#
# with open('templates/service.txt','r') as f:
#     service_template = f.read()
#
# with open('templates/schema.txt','r') as f:
#     schema_template = f.read()
#
# with open('templates/model.txt','r') as f:
#     model_template = f.read()
#
# with open('templates/router.txt','r') as f:
#     router_template = f.read()
#
# with open('templates/router_import.txt','r') as f:
#     router_import_template = f.read()
#
# with open('templates/router_connect.txt','r') as f:
#     router_connect_template = f.read()
#
# with open('templates/test_repository.txt','r') as f:
#     test_repository_template = f.read()
#
# with open('templates/test_service.txt','r') as f:
#     test_service_template = f.read()
templates = {}
filenames = [
    'repository', 'service', 'schema', 'model', 'router',
    'router_import', 'router_connect', 'test_repository', 'test_service'
]

for name in filenames:
    with open(f'code_schemas/{name}.txt', 'r') as f:
        templates[f'{name}_template'] = f.read()

# Access the templates
repository_template = templates['repository_template']
service_template = templates['service_template']
schema_template = templates['schema_template']
model_template = templates['model_template']
router_template = templates['router_template']
router_import_template = templates['router_import_template']
router_connect_template = templates['router_connect_template']
test_repository_template = templates['test_repository_template']
test_service_template = templates['test_service_template']


# Function to create directory if it does not exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


entities = ['user1']

# Main script
for entity in entities:
    entity_lower = entity.lower()
    entity_capitalized = entity.capitalize()

    # Create directories
    for directory in directories:
        dir_path = os.path.join(directory, entity_lower)
        create_directory(dir_path)

    # Write files with the corresponding content
    files_content = {
        f'repositories/{entity_lower}/{entity_lower}_repository.py': repository_template.format(entity=entity_lower,
                                                                                                Entity=entity_capitalized),
        f'services/{entity_lower}/{entity_lower}_service.py': service_template.format(entity=entity_lower,
                                                                                      Entity=entity_capitalized),
        f'schemas/{entity_lower}/{entity_lower}_schema.py': schema_template.format(entity=entity_lower,
                                                                                   Entity=entity_capitalized),
        f'database/models/{entity_lower}/{entity_lower}.py': model_template.format(entity=entity_lower,
                                                                                   Entity=entity_capitalized),
        f'routers/{entity_lower}/{entity_lower}_router.py': router_template.format(entity=entity_lower,
                                                                                   Entity=entity_capitalized),
        f'tests/{entity_lower}/test_{entity_lower}_repository.py': test_repository_template.format(
            entity=entity_lower,
            Entity=entity_capitalized),
        f'tests/{entity_lower}/test_{entity_lower}_service.py': test_service_template.format(entity=entity_lower,
                                                                                             Entity=entity_capitalized),
    }
    # Fill entity files
    for file_path, content in files_content.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write(content)

# Connect to general FastAPI router
init_content_lines = ["from fastapi import APIRouter"] + [router_import_template.format(entity=ent.lower()) for ent
                                                          in
                                                          entities] + ["router = APIRouter()"] + [
                         router_connect_template.format(entity=ent.lower(), Entity=ent.capitalize()) for ent in
                         entities]
with open('routers/__init__.py', 'w') as file:
    file.write("\n".join(init_content_lines))
