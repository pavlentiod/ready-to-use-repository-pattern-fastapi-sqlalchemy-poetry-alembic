import os
import sys




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
repository_template = ''' 
import asyncio
from typing import List, Optional, Type

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from database.models.{entity}.{entity} import {Entity}
from schemas.{entity}.{entity}_schema import {Entity}Input, {Entity}Output


class {Entity}Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: {Entity}Input) -> {Entity}Output:
        entity = {Entity}()
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return {Entity}Output(
            id=entity.id)

    async def get_all(self) -> List[Optional[{Entity}Output]]:
        stmt = select({Entity}).order_by({Entity}.id)
        result = await self.session.execute(stmt)
        entities = result.scalars().all()
        return [{Entity}Output(**entity.__dict__) for entity in entities]

    async def get_{entity}(self, _id: UUID4) -> {Entity}Output:
        entity = await self.session.get({Entity}, _id)
        return {Entity}Output(**entity.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[{Entity}]:
        return await self.session.get({Entity}, _id)

    async def update(self, entity: Type[{Entity}], data: {Entity}Input) -> {Entity}Output:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(entity, key, value)
        await self.session.commit()
        await self.session.refresh(entity)
        return {Entity}Output(**entity.__dict__)

    async def delete(self, entity: Type[{Entity}]) -> bool:
        await self.session.delete(entity)
        await self.session.commit()
        return True

'''

service_template = '''
import asyncio
import datetime
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from repositories.{entity}.{entity}_repository import {Entity}Repository
from schemas.{entity}.{entity}_schema import {Entity}Input, {Entity}Output, {Entity}Endpoint


class {Entity}Service:
    """
    Service class for handling {Entity}s.
    """

    def __init__(self, session: AsyncSession):
        self.repository = {Entity}Repository(session)

    async def create(self, data: {Entity}Endpoint) -> {Entity}Output:
        entity_output = await self.repository.create(data)
        return entity_output

    async def get_all(self) -> List[{Entity}Output]:
        return await self.repository.get_all()

    async def get_{entity}(self, _id: UUID4) -> {Entity}Output:
        entity = await self.repository.get_by_id(_id)
        if not entity:
            raise HTTPException(status_code=404, detail="{Entity} not found")
        return entity

    async def update(self, _id: UUID4, data: {Entity}Input) -> {Entity}Output:
        entity = await self.repository.get_by_id(_id)
        if not entity:
            raise HTTPException(status_code=404, detail="{Entity} not found")
        updated_entity = await self.repository.update(entity, data)
        return updated_entity

    async def delete(self, _id: UUID4) -> bool:
        entity = await self.repository.get_by_id(_id)
        if not entity:
            raise HTTPException(status_code=404, detail="{Entity} not found")
        return await self.repository.delete(entity)


async def main():
    async with db_helper.session_factory() as session:
        pass

if __name__ == "__main__":
    asyncio.run(main())
'''

schema_template = '''
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

class {Entity}Input(BaseModel):
    pass

class {Entity}Output(BaseModel):
    id: UUID

class {Entity}Endpoint(BaseModel):
    pass
'''

model_template = '''
from sqlalchemy import String, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

class {Entity}(Base):
    __tablename__ = "{entity}"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    some_column_str: Mapped[str] = mapped_column(String(100), nullable=True, server_default='', default='')
    some_column_int: Mapped[int] = mapped_column(Integer, nullable=False)

    some_relationship_column: Mapped[int] = mapped_column(ForeignKey("other_model.key"))
    some_relationship: Mapped["Other_model"] = relationship(back_populates="other_model_relationship")
'''

router_template = '''
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import UUID4

from database import db_helper
from services.{entity}.{entity}_service import {Entity}Service
from schemas.{entity}.{entity}_schema import {Entity}Input, {Entity}Output

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED, response_model={Entity}Output)
async def create_{entity}(
        data: {Entity}Input,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = {Entity}Service(session)
    return await _service.create(data)

@router.get("", status_code=status.HTTP_200_OK, response_model=List[{Entity}Output])
async def get_{entity}s(session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> List[{Entity}Output]:
    _service = {Entity}Service(session)
    return await _service.get_all()

@router.get("/{{_id}}", status_code=status.HTTP_200_OK, response_model={Entity}Output)
async def get_{entity}(
        _id: UUID4,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = {Entity}Service(session)
    return await _service.get_{entity}(_id)

@router.put("/{{_id}}", status_code=status.HTTP_200_OK, response_model={Entity}Output)
async def update_{entity}(
        _id: UUID4,
        data: {Entity}Input,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = {Entity}Service(session)
    return await _service.update(_id, data)

@router.delete("/{{_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{entity}(
        _id: UUID4,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = {Entity}Service(session)
    await _service.delete(_id)
    # return {{"detail" : "... deleted successfully"}}
    return "deleted"
'''

router_import_template = """
from .{entity}.{entity}_router import router as {entity}_router
"""
router_connect_template = """
router.include_router({entity}_router, prefix='/{entity}', tags=['{Entity}'])
"""

test_repository_template = """
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.{entity}.{entity}_repository import {Entity}Repository
from schemas.{entity}.{entity}_schema import {Entity}Input


@pytest.fixture
def sample_{entity}_data() -> {Entity}Input:
    return {Entity}Input(
        # Add sample data fields here
    )

@pytest.fixture
def updated_{entity}_data() -> {Entity}Input:
    return {Entity}Input(
        # Add updated data fields here
    )


async def test_create(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    {entity}_repository = {Entity}Repository(session=session)
    {entity} = await {entity}_repository.create(sample_{entity}_data)

    assert {entity}.field == sample_{entity}_data.field  # Replace 'field' with actual field names

async def test_get_all(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    {entity}_repository = {Entity}Repository(session=session)
    await {entity}_repository.create(sample_{entity}_data)
    {entity}s = await {entity}_repository.get_all()

    assert len({entity}s) > 0
    assert {entity}s[0].field == sample_{entity}_data.field  # Replace 'field' with actual field names

async def test_get_{entity}(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    {entity}_repository = {Entity}Repository(session=session)
    created_{entity} = await {entity}_repository.create(sample_{entity}_data)
    {entity} = await {entity}_repository.get_{entity}(created_{entity}.id)

    assert {entity}.field == sample_{entity}_data.field  # Replace 'field' with actual field names
    assert {entity}.id == created_{entity}.id

async def test_get_by_id(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    {entity}_repository = {Entity}Repository(session=session)
    created_{entity} = await {entity}_repository.create(sample_{entity}_data)
    {entity} = await {entity}_repository.get_by_id(created_{entity}.id)

    assert {entity} is not None
    assert {entity}.id == created_{entity}.id

async def test_update(session: AsyncSession, sample_{entity}_data: {Entity}Input, updated_{entity}_data: {Entity}Input):
    {entity}_repository = {Entity}Repository(session=session)
    created_{entity} = await {entity}_repository.create(sample_{entity}_data)
    {entity} = await {entity}_repository.get_by_id(created_{entity}.id)
    updated_{entity} = await {entity}_repository.update({entity}, updated_{entity}_data)

    assert updated_{entity}.field == updated_{entity}_data.field  # Replace 'field' with actual field names

async def test_delete(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    {entity}_repository = {Entity}Repository(session=session)
    created_{entity} = await {entity}_repository.create(sample_{entity}_data)
    {entity} = await {entity}_repository.get_by_id(created_{entity}.id)
    success = await {entity}_repository.delete({entity})

    assert success is True
"""

test_service_template = """
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from schemas.{entity}.{entity}_schema import {Entity}Input
from service.{entity}.{entity}_service import {Entity}Service


@pytest.fixture
def sample_{entity}_data() -> {Entity}Input:
    return {Entity}Input(
        # Add sample data fields here
    )

@pytest.fixture
def updated_{entity}_data() -> {Entity}Input:
    return {Entity}Input(
        # Add updated data fields here
    )

async def test_create_{entity}(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    service = {Entity}Service(session)

    # Create a new {entity}
    created_{entity} = await service.create(sample_{entity}_data)

    # Verify the created {entity} has the expected attributes
    assert created_{entity}.field == sample_{entity}_data.field  # Replace 'field' with actual field names

    # Try to create the same {entity} again (should raise HTTPException)
    # with pytest.raises(HTTPException):
    #     await service.create(sample_{entity}_data)

    # Clean up by deleting the created {entity} (if necessary)
    await service.delete(created_{entity}.id)


async def test_get_all_{entity}s(session: AsyncSession):
    service = {Entity}Service(session)

    # Retrieve all {entity}s (expecting at least one)
    all_{entity}s = await service.get_all()
    assert len(all_{entity}s) > 0

    # Clean up by deleting all {entity}s (if necessary)
    for {entity} in all_{entity}s:
        await service.delete({entity}.id)


async def test_get_{entity}_by_id(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    service = {Entity}Service(session)

    # Create a new {entity}
    created_{entity} = await service.create(sample_{entity}_data)

    # Retrieve the {entity} by ID
    retrieved_{entity} = await service.get_{entity}(created_{entity}.id)

    # Verify the retrieved {entity} matches the created {entity}
    assert retrieved_{entity}.field == sample_{entity}_data.field  # Replace 'field' with actual field names

    # Try to retrieve a non-existent {entity} (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.get_{entity}(uuid4())

    # Clean up by deleting the created {entity}
    await service.delete(created_{entity}.id)


async def test_update_{entity}(session: AsyncSession, sample_{entity}_data: {Entity}Input, updated_{entity}_data: {Entity}Input):
    service = {Entity}Service(session)

    # Create a new {entity}
    created_{entity} = await service.create(sample_{entity}_data)

    # Update the {entity}'s information
    updated_{entity} = await service.update(created_{entity}.id, updated_{entity}_data)

    # Verify the updated {entity} has the new attributes
    assert updated_{entity}.field == updated_{entity}_data.field  # Replace 'field' with actual field names

    # Try to update a non-existent {entity} (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.update(uuid4(), updated_{entity}_data)

    # Clean up by deleting the created {entity}
    await service.delete(created_{entity}.id)


async def test_delete_{entity}(session: AsyncSession, sample_{entity}_data: {Entity}Input):
    service = {Entity}Service(session)

    # Create a new {entity}
    created_{entity} = await service.create(sample_{entity}_data)

    # Delete the {entity} and verify
    result = await service.delete(created_{entity}.id)
    assert result is True

    # Try to delete a non-existent {entity} (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.delete(uuid4())

    # Clean up by deleting the created {entity} (if necessary)
    # Note: Depending on your implementation, the {entity} might already be deleted in the previous step.
"""


# Function to create directory if it does not exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == "__main__":
    # List of entities
    # entities = [i for i in sys.argv]
    entities = ['user']

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