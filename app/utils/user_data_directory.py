# https://gist.github.com/jslay88/1fd8a8ba1d05ff2a4810520785a67891
# Copyright jslay88 on Github (https://jslay.net/)


import sys
import logging
import pathlib
from typing import Optional, Union, List, Tuple


logger = logging.getLogger(__name__)


def get_user_data_dir(
    appending_paths: Union[str, List[str], Tuple[str, ...]] = None
) -> pathlib.Path:
    """
    Returns a parent directory path where persistent application data can be stored.
    Can also append additional paths to the return value automatically.

    Linux: ~/.local/share
    macOS: ~/Library/Application Support
    Windows: C:/Users/<USER>/AppData/Roaming

    :param appending_paths: Additional path (str) or paths (List[str], Tuple[str]) to append to return value
    :type appending_paths: Un

    :return: User Data Path
    :rtype: str
    """
    logger.debug(f"Getting Home Path...")
    home = pathlib.Path.home()
    logger.debug(f"Home Path: {home}")

    system_paths = {
        "win32": home / "AppData/Roaming",
        "linux": home / ".local/share",
        "darwin": home / "Library/Application Support",
    }

    logger.debug(f"Getting System Platform...")
    if sys.platform not in system_paths:
        raise SystemError(
            f'Unknown System Platform: {sys.platform}. Only supports {", ".join(list(system_paths.keys()))}'
        )
    data_path = system_paths[sys.platform]

    if appending_paths:
        if isinstance(appending_paths, str):
            appending_paths = [appending_paths]
        for path in appending_paths:
            data_path = data_path / path

    logger.debug(f"System Platform: {sys.platform}")
    logger.debug(f"User Data Directory: {system_paths[sys.platform]}")
    logger.debug(f"Return Value: {data_path}")
    return data_path
