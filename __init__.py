from tools.code_tools import (
    code_structure_analyzer,
    bug_detector,
    best_practices_checker,
    code_improver,
)
from tools.cv_tools import cv_analyzer
from tools.search_tool import web_search

ALL_TOOLS = [
    code_structure_analyzer,
    bug_detector,
    best_practices_checker,
    code_improver,
    cv_analyzer,
    web_search,
]
