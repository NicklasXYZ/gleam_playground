import re
from common.common import get_secret

# 7-bit C1 ANSI sequences (used for removing rebar3 terminal colors and styling)
ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


API_KEY = get_secret("API_KEY")
GLEAM_PROJECT_NAME = 'gleam_project'
GLEAM_PROJECT_FILE = f'{GLEAM_PROJECT_NAME}/src/{GLEAM_PROJECT_NAME}.gleam'