import configparser
import os
import typing

from flytekit.configuration import common as _config_common
from flytekit.configuration.common import format_section


def get_specified_images() -> typing.Dict[str, str]:
    """
    This section should contain options, where the option name is the friendly name of the image and the corresponding
    value is actual FQN of the image. Example of how the section is structured
    [images]
    my_image1=docker.io/flyte:tag
    # Note that the tag is optional. If not specified it will be the default version identifier specified
    my_image2=docker.io/flyte

    :returns a dictionary of name: image<fqn+version> Version is optional
    """

    images: typing.Dict[str, str] = {}

    # Try reading images from env vars first.
    image_section = format_section("image")
    for env_var in os.environ.keys():
        if env_var.startswith(image_section):
            images[env_var.split("_")[-1]] = os.getenv(env_var)

    if _config_common.CONFIGURATION_SINGLETON.config is None:
        print("No config file specified, will use the default image")
        return images
    try:
        image_names = _config_common.CONFIGURATION_SINGLETON.config.options("images")
    except configparser.NoSectionError:
        print("No images specified, will use the default image")
        image_names = None

    if not image_names:
        return images

    for i in image_names:
        if i not in images:
            images[str(i)] = _config_common.FlyteStringConfigurationEntry("images", i).get()
    return images
