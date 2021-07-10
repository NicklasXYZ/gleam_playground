from typing import Optional, Union, Tuple
import logging
import json
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.params import Header
from starlette.responses import Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware 
from database import redis_cache
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud, models, schemas
from common.middleware import ContentSizeLimitMiddleware
from common.common import check_api_key, load_cors
from settings import (
    API_KEY,
    VERSION,
    REDIS_TTL,
    SNIPPET_DIR,
)


app = FastAPI(docs_url = None, redoc_url = None)
CORS_CONFIG = load_cors()
if CORS_CONFIG:
    app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Limit request size to 250000 bytes ~ 0.25 megabytes
app.add_middleware(ContentSizeLimitMiddleware, max_content_size = 25_00_00)

# Create database tables
models.Base.metadata.create_all(bind = engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def read_snippet(filepath: str) -> Union[None, str]:    
    """Read in a Gleam code snippet from local file storage.

    Args:
        filepath (str): The filepath to a Gleam code snippet.

    Returns:
        Union[None, bool]: True if the Gleam code snippet was read in and cached
            correctly. Otherwise None or False.
    """
    with open(filepath) as f:
        name = None; uuid = None
        print("Reading in snippet: ")
        while True:
            try:
                line = next(f)
                if len(line.split("//cname:")) == 2:
                    name = line.split("//cname:")[-1].strip("'\n")
                if len(line.split("//cuuid:")) == 2:
                    uuid = line.split("//cuuid:")[-1].strip("'\n")
                if name is not None and uuid is not None:
                    code = str(f.read())
                    # Cache the Gleam code snippet in Redis
                    rc = await redis_cache.set(
                        key = uuid,
                        value = json.dumps(code),
                        expire = REDIS_TTL,
                    )
                    if rc is None:
                        logging.debug(
                            f'REDIS: A Gleam code snippet could not be cached with identifier: {uuid}'
                        )
                    return code
            except StopIteration:
                break
    return None


async def check_snippets(key: str) -> Union[None, str]:
    """Check local storage for a certain Gleam code snippet.

    Args:
        key (str): The identifier of a Gleam code snippet to be retrieved.

    Returns:
        Union[None, str]: A filepath if successful. Otherwise None.
    """
    gleam_files = [f for f in os.listdir(SNIPPET_DIR) if "gleam" in f.split(".")]
    for gleam_file in gleam_files:
        filepath = os.path.join(SNIPPET_DIR, gleam_file)
        with open(filepath) as f:
            name = None; uuid = None
            while True:
                try:
                    line = next(f)
                    if len(line.split("//cname:")) == 2:
                        name = line.split("//cname:")[-1].strip("'\n")
                        print("Name: ", name)
                    if len(line.split("//cuuid:")) == 2:
                        uuid = line.split("//cuuid:")[-1].strip("'\n")
                        print("UUID: ", uuid)
                    if name is not None and uuid is not None:
                        if uuid == key:
                            return filepath
                except StopIteration:
                    break
    return None


@app.get('/version')
async def version() -> Response:
    return Response(VERSION, 200)


@app.options('/version')
async def version_options() -> Response:
    """... Send a default preflight request response...

    Returns:
        Response: ...
    """
    return Response(
        'Success', 200, 
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*'
        }
    )

    
@app.on_event('startup')
async def starup_event() -> None:
    await redis_cache.init_cache()


@app.on_event('shutdown')
async def shutdown_event() -> None:
    redis_cache.close()
    await redis_cache.wait_closed()


@app.post('/snippet')
async def create_snippet(
    snippet: schemas.BaseSnippet,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None),
    ) -> JSONResponse:
    """Create a Gleam code snippet and save it for long term storage.

    Args:
        snippet (schemas.BaseSnippet): A Gleam code snippet that is to be saved to the database.
        db (Session, optional): A database session. Defaults to Depends(get_db).
        x_api_key (Optional[str], optional): An API key provided by the frontend.
            Defaults to Header(None).

    Returns:
        JSONResponse: The identifier of the saved code snippet.
    """
    # Check if the given API is valid
    check_api_key(x_api_key, API_KEY)
    db_snippet = crud.create_snippet(db = db, snippet = snippet)
    logging.debug(
        f'DB   : A Gleam code snippet was created with identifier: {db_snippet.snippetID}'
    )
    code = json.dumps(db_snippet.code)
    # Cache the Gleam code snippet
    rc = await redis_cache.set(
        key = db_snippet.snippetID,
        value = code,
        expire = REDIS_TTL,
    )
    if rc is not None:
        logging.debug(
            f'REDIS: A Gleam code snippet was cached with identifier: {db_snippet.snippetID}'
        )
    rv = {'snippetID': db_snippet.snippetID}
    return JSONResponse(rv, 201)


@app.options('/snippet')
async def snippet_options() -> Response:
    """... Send a default preflight request response...

    Returns:
        Response: ...
    """
    return Response(
        'Success', 200, 
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*'
        }
    )


@app.get('/snippet/{snippet_id}')
async def get_snippet(
    snippet_id: str,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None),
    ) -> JSONResponse:
    """Retrieve a Gleam code snippet given a certain identifier.

    Args:
        snippet_id (str): The identifier of the saved Gleam code snippet.
        db (Session, optional): A database session. Defaults to Depends(get_db).
        x_api_key (Optional[str], optional): An API key provided by the frontend.
            Defaults to Header(None).

    Raises:
        HTTPException: If the requested Gleam code snippet was not found.

    Returns:
        JSONResponse: The requested Gleam code snippet.
    """
    # Check if the given API is valid
    check_api_key(x_api_key, API_KEY)
    # Try to retrieve the Gleam code snippet from cache
    code = await redis_cache.get(key = snippet_id)
    if code is None:
            # Try to retrieve the Gleam code snippet from the database
            db_snippet = crud.get_snippet(db, snippet_id = snippet_id)
            logging.debug(
                f'DB   : A Gleam code snippet was retrieved with identifier: {snippet_id}'
            )
            if db_snippet is None:
                # As a last resort, try to retrieve the Gleam code snippet from local file storage
                filepath = await check_snippets(key = snippet_id)
                if filepath is not None:
                    code = await read_snippet(filepath = filepath)
                else:
                    logging.debug(
                        f'     : No Gleam code snippet could be found with identifier: {snippet_id}'
                    )
                    raise HTTPException(status_code = 404, detail = 'Snippet not found')
            else:
                code = db_snippet.code
    else:
        logging.debug(
            f'REDIS: A Gleam code snippet was retrieved with identifier: {snippet_id}'
        )
        code = json.loads(code)
    rv = {'fileName': None, 'code': code}
    return JSONResponse(rv, 200)