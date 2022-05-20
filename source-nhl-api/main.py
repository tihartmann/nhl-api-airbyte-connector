#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nhl_api import SourceNhlApi

if __name__ == "__main__":
    source = SourceNhlApi()
    launch(source, sys.argv[1:])
