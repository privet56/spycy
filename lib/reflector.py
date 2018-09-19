import json
import os, sys
import re
import random

import inspect
import logging
import traceback

class Reflector:

    @staticmethod
    def get_function_name():
        return traceback.extract_stack(None, 2)[0][2]
