import os

# Directories to be created
import sys


# Function to create directory if it does not exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs("src/" + path)


if __name__ == "__main__":
    directories = [
        'repositories',
        'services',
        'routers',
        'schemas',
        'tests',
        'database/models'
    ]

    templates = {}
    filenames = [
        'repository', 'service', 'schema', 'model', 'router',
        'test_repository', 'test_service'
    ]

    for name in filenames:
        with open(f'templates/{name}.txt', 'r') as f:
            templates[f'{name}_template'] = f.read()

    # Access the templates
    repository_template = templates['repository_template']
    service_template = templates['service_template']
    schema_template = templates['schema_template']
    model_template = templates['model_template']
    router_template = templates['router_template']
    test_repository_template = templates['test_repository_template']
    test_service_template = templates['test_service_template']

    entities = [i for i in sys.argv[1:]]
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
                with open(f"src/{file_path}", 'w') as file:
                    file.write(content)

    # Connect to general FastAPI router
    init_content_lines = ["from fastapi import APIRouter"] + [
        "from .{entity}.{entity}_router import router as {entity}_router".format(entity=ent.lower()) for ent
        in
        entities] + ["router = APIRouter()"] + [
                             "router.include_router({entity}_router, prefix='/{entity}', tags=['{Entity}'])".format(
                                 entity=ent.lower(), Entity=ent.capitalize()) for ent in
                             entities]
    if not os.path.exists('src/routers/__init__.py'):
        with open('src/routers/__init__.py', 'w') as file:
            file.write("\n".join(init_content_lines))

    # Connect models to DB metadata
    init_models_lines = ["__all__=("]
    init_models_lines.extend([f'"{ent.capitalize()}"' for ent in entities])
    init_models_lines.extend([')\n\n'])
    init_models_lines.extend(["from .base import Base", "from .db_helper import DatabaseHelper, db_helper"])
    init_models_lines.extend([f"from .models.{ent.lower()}.{ent.lower()} import {ent.capitalize()}" for ent in entities])

    if not os.path.exists('src/database/__init__.py'):
        with open('src/database/__init__.py', 'w') as file:
            file.write("\n".join(init_models_lines))