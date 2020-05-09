"""Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

ADB Debugging must be enabled.
"""

from .androidtv import AndroidTV
from .basetv import BaseTV, state_detection_rules_validator
from .constants import DEFAULT_AUTH_TIMEOUT_S
from .firetv import FireTV


__version__ = '0.0.1'


async def setup(host, port=5555, adbkey='', state_detection_rules=None, device_class='auto', auth_timeout_s=DEFAULT_AUTH_TIMEOUT_S):
    """Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

    Parameters
    ----------
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication
    adb_server_ip : str
        The IP address of the ADB server
    adb_server_port : int
        The port for the ADB server
    state_detection_rules : dict, None
        A dictionary of rules for determining the state (see :class:`~aio_androidtv.basetv.BaseTV`)
    device_class : str
        The type of device: ``'auto'`` (detect whether it is an Android TV or Fire TV device), ``'androidtv'``, or ``'firetv'```
    auth_timeout_s : float
        Authentication timeout (in seconds)

    Returns
    -------
    aftv : AndroidTV, FireTV
        The representation of the device

    """
    if device_class == 'androidtv':
        atv = AndroidTV(host, port, adbkey, state_detection_rules)
        await atv.adb_connect(auth_timeout_s=auth_timeout_s)
        atv.device_properties = await atv.get_device_properties()
        return atv

    if device_class == 'firetv':
        ftv = FireTV(host, port, adbkey, state_detection_rules)
        await ftv.adb_connect(auth_timeout_s=auth_timeout_s)
        ftv.device_properties = await ftv.get_device_properties()
        return ftv

    if device_class != 'auto':
        raise ValueError("`device_class` must be 'androidtv', 'firetv', or 'auto'.")

    aftv = BaseTV(host, port, adbkey, state_detection_rules)

    # establish the ADB connection
    await aftv.adb_connect(auth_timeout_s=auth_timeout_s)

    # get device properties
    aftv.device_properties = await aftv.get_device_properties()

    # Fire TV
    if aftv.device_properties.get('manufacturer') == 'Amazon':
        aftv.__class__ = FireTV

    # Android TV
    else:
        aftv.__class__ = AndroidTV

    return aftv


def ha_state_detection_rules_validator(exc):
    """Validate the rules (i.e., the ``state_detection_rules`` value) for a given app ID (i.e., a key in ``state_detection_rules``).

    See :class:`~aio_androidtv.basetv.BaseTV` for more info about the ``state_detection_rules`` parameter.

    Parameters
    ----------
    exc : Exception
        The exception that will be raised if a rule is invalid

    Returns
    -------
    wrapped_state_detection_rules_validator : function
        A function that is the same as :func:`~aio_androidtv.basetv.state_detection_rules_validator`, but with the ``exc`` argument provided

    """
    def wrapped_state_detection_rules_validator(rules):
        """Run :func:`~aio_androidtv.basetv.state_detection_rules_validator` using the ``exc`` parameter from the parent function."""
        return state_detection_rules_validator(rules, exc)

    return wrapped_state_detection_rules_validator
