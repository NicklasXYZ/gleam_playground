import asyncio 
import shutil
import logging
import os
from tempfile import TemporaryDirectory
from typing import Optional
from typing import Union, List, Dict, Any, Tuple
from fastapi import FastAPI, Request, HTTPException
from fastapi.params import Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware 
from common.middleware import ContentSizeLimitMiddleware

from common.common import check_api_key, str_to_bool_or_none, load_cors
from settings import (
    ansi_escape,
    API_KEY,
    GLEAM_PROJECT_NAME,
    GLEAM_PROJECT_FILE,
)


# Local type alias
Events = List[Dict[str, Any]]


# Parameters & settings
logging.basicConfig(level = logging.DEBUG)
app = FastAPI(docs_url = None, redoc_url = None)
CORS_CONFIG = load_cors()
if CORS_CONFIG:
    app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Limit request size to 250000 bytes = 0.25 megabytes
app.add_middleware(ContentSizeLimitMiddleware, max_content_size=25_00_00)


async def run_subprocess(
    commandline_args: str,
    cwd: Union[None, str],
    ) -> Tuple[List[str], List[str], int]:
    """Run shell commands.

    Args:
        commandline_args (str): Shell commands to be run.
        cwd (Union[None, str], optional): The current working directory. Defaults to
            None.

    Returns:
        Tuple[List[str], List[str], int]: stdout, stderror and a return code
    """
    logging.debug('Subprocess commandline args: ' + commandline_args)
    s = await asyncio.create_subprocess_shell(
        commandline_args,
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.STDOUT,
        cwd = cwd,
    )
    stdout_data, stderr_data = await s.communicate()
    logging.debug('\nSubprocess stdout: ')
    for string in stdout_data.decode('utf-8').split('\n'):
        logging.debug(string)
    logging.debug('\nSubprocess stderr: ')
    for string in str(stderr_data).split('\n'):
        logging.debug(string)
    # Check the returncode to see whether the process terminated normally
    if s.returncode == 0:
        logging.debug(
            'Subprocess exited normally with return code: ' + str(s.returncode)
            )
        return stdout_data.decode('utf-8').split('\n'), str(stderr_data).split('\n'), 0
    else:
        logging.debug(
            'Subprocess exited with non-zero return code: ' + str(s.returncode)
        )
        return stdout_data.decode('utf-8').split('\n'), str(stderr_data).split('\n'), -1


async def handle_output(
    stdout: List[str],
    stderr: List[str],
    ) -> Events:
    """Organize stdout and stderr for a frontend application to consume.

    Args:
        stdout (List[str]): Standard output resulting from running a command in a shell.
        stderr (List[str]): Error output resulting from running a command in a shell.

    Returns:
        Events: Organized stdout and stderr output.
    """
    events = []
    events.extend([
            {
                'Message': ansi_escape.sub('', _),
                'Kind': 'stdout',
                # NOTE: Delay is currently not used
                'Delay': 0,
            } for _ in stdout
        ]
    )
    if stderr is None:
        events.append(
            {
                'Message': ansi_escape.sub('', stderr),
                'Kind': 'stderr',
                # NOTE: Delay is currently not used
                'Delay': 0,
            }
        )
    return events


@app.post('/run')
async def run(
    request: Request,
    x_api_key: Optional[str] = Header(None),
    ) -> JSONResponse:
    """Compile and run a gleam code snippet.

    Args:
        request (Request): A request containing a Gleam code snippet that is
            to be compilled and run.
        x_api_key (Optional[str], optional): An API key provided by the frontend.
            Defaults to Header(None).

    Raises:
        HTTPException: If the backend can not find the appropriate files that is to be
            compilled and run.

    Returns:
        JSONResponse: The formatted code, stderr and stdout associated with the 
            execution of the Gleam code snippet.
    """
    # Check if the given API is valid
    check_api_key(x_api_key, API_KEY)
    result = await request.json()
    events = []; formatted = None
    # Create a temporary directory for compiling and running a Gleam snippet
    with TemporaryDirectory() as td:
        # Copy a default and pre-defined Gleam project to the temporary directory
        shutil.copytree(
            f'./{GLEAM_PROJECT_NAME}',
            f'{td}/{GLEAM_PROJECT_NAME}',
            copy_function = shutil.copy,
        )
        # Check that everything was copied properly to the temporary directory
        if os.path.exists(f'{td}/{GLEAM_PROJECT_NAME}'):
            # Write the Gleam code snippet we would like to run to a file in the
            # default Gleam project  
            with open(f'{td}/{GLEAM_PROJECT_FILE}', 'w') as f:
                f.write(result['code'])
            # Compile the given Gleam code snippet
            stdout, stderr, rc = await run_subprocess(
                f'export HOME={td} && rebar3 escriptize',
                cwd = f'{td}/{GLEAM_PROJECT_NAME}'
            )
            # Save all events from stdout and stderr such that we can forward these to 
            # the user in the frontend
            events_ = await handle_output(stdout, stderr)
            events.extend(events_)
            # If the Gleam project was compilled successfully then try to run the code
            if rc == 0:
                stdout, stderr, rc = await run_subprocess(
                    f'_build/default/bin/{GLEAM_PROJECT_NAME}',
                    cwd = f'{td}/{GLEAM_PROJECT_NAME}',
                )
                # Again, save all events from stdout and stderr such that we can forward
                # these to the user in the frontend
                events_ = await handle_output(stdout, stderr)
                events.extend(events_)
                if "format" in request.query_params:
                    if str_to_bool_or_none(request.query_params["format"]) == True:
                        # Finally, format the gleam code
                        events_, formatted = await _format(td = td)
                        events.extend(events_) 
        # ... Else raise an exception and log the attempt
        else:
            logging.debug('A Gleam code snippet could not be compilled...')
            logging.debug(f'Temp dir: {td}')
            raise HTTPException(
                status_code = 500,
                detail = 'The Gleam code snippet could not be compilled by the backend',
            )
    # Return formatted code and associated events (stdout and stderr)
    if formatted is not None:
        response = {'events': events, 'formatted': formatted}
    else:
        response = {'events': events}
    return JSONResponse(response, 200)


async def _format(td: str) -> Tuple[Events, str]:
    """Run the 'gleam format' command in a shell in the directory that contains a given
    Gleam code snippet.

    Args:
        td (str): The temporary directory containing the Gleam code snippet that is to
            be formatted.

    Returns:
        Tuple[Events, str]: Stdout, stderror and the formatted code (if no errors were
            encountered).
    """
    events = []; formatted = None
    stdout, stderr, _ = await run_subprocess(
        f'gleam format',
        cwd = f'{td}/{GLEAM_PROJECT_NAME}'
    )
    with open(f'{td}/{GLEAM_PROJECT_FILE}', 'r') as f:
        formatted = f.read()
    events_ = await handle_output(stdout, stderr)
    events.extend(events_)
    return events, formatted


@app.post('/format')
async def format(
    request: Request,
    x_api_key: Optional[str] = Header(None),
    ) -> JSONResponse:
    """Format a given Gleam code snippet and return the formatted code (if no errors were
    encountered).

    Args:
        request (Request): Request containing the Gleam code snippet to be formatted.
        x_api_key (Optional[str], optional): An API key provided by the frontend.
            Defaults to Header(None).

    Raises:
        HTTPException: If the backend can not find the appropriate files that is to be
            formatted.

    Returns:
        JSONResponse: Stdout, stderror and the formatted code (if no errors were
            encountered).
    """
    # Check if the given API is valid
    check_api_key(x_api_key, API_KEY)
    result = await request.json()
    events = []; formatted = None
    # Create a temporary directory for running 'gleam format' in a temporary
    # project directory
    with TemporaryDirectory() as td:
        # Copy default project structure to temporary directory
        shutil.copytree(
            f'./{GLEAM_PROJECT_NAME}',
            f'{td}/{GLEAM_PROJECT_NAME}',
            copy_function = shutil.copy,
        )   
        # Check that everything was copied in properly
        if os.path.exists(f'{td}/{GLEAM_PROJECT_NAME}'):
            with open(f'{td}/{GLEAM_PROJECT_FILE}', 'w') as f:
                f.write(result['code'])
            events_, formatted = await _format(td = td)
            events.extend(events_) 
        # ... Else raise an exception and log the attempt
        else:
            logging.debug('A Gleam code snippet could not be formatted...')
            logging.debug(f'Temp dir: {td}')
            raise HTTPException(
                status_code = 500,
                detail = 'The Gleam code snippet could not be formatted by the backend',
            )
    # Return formatted code and associated events (stdout and stderr)
    response = {'formatted': formatted, 'events': events}
    return JSONResponse(response, 200)