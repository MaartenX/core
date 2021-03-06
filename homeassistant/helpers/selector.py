"""Selectors for Home Assistant."""
from typing import Any, Callable, Dict, cast

import voluptuous as vol

from homeassistant.const import CONF_MODE, CONF_UNIT_OF_MEASUREMENT
from homeassistant.util import decorator

SELECTORS = decorator.Registry()


def validate_selector(config: Any) -> Dict:
    """Validate a selector."""
    if not isinstance(config, dict):
        raise vol.Invalid("Expected a dictionary")

    if len(config) != 1:
        raise vol.Invalid(f"Only one type can be specified. Found {', '.join(config)}")

    selector_type = list(config)[0]

    selector_class = SELECTORS.get(selector_type)

    if selector_class is None:
        raise vol.Invalid(f"Unknown selector type {selector_type} found")

    # Seletors can be empty
    if config[selector_type] is None:
        return {selector_type: {}}

    return {
        selector_type: cast(Dict, selector_class.CONFIG_SCHEMA(config[selector_type]))
    }


class Selector:
    """Base class for selectors."""

    CONFIG_SCHEMA: Callable


@SELECTORS.register("entity")
class EntitySelector(Selector):
    """Selector of a single entity."""

    CONFIG_SCHEMA = vol.Schema(
        {
            # Integration that provided the entity
            vol.Optional("integration"): str,
            # Domain the entity belongs to
            vol.Optional("domain"): str,
            # Device class of the entity
            vol.Optional("device_class"): str,
        }
    )


@SELECTORS.register("device")
class DeviceSelector(Selector):
    """Selector of a single device."""

    CONFIG_SCHEMA = vol.Schema(
        {
            # Integration linked to it with a config entry
            vol.Optional("integration"): str,
            # Manufacturer of device
            vol.Optional("manufacturer"): str,
            # Model of device
            vol.Optional("model"): str,
        }
    )


@SELECTORS.register("number")
class NumberSelector(Selector):
    """Selector of a numeric value."""

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Required("min"): vol.Coerce(float),
            vol.Required("max"): vol.Coerce(float),
            vol.Optional("step", default=1): vol.All(
                vol.Coerce(float), vol.Range(min=1e-3)
            ),
            vol.Optional(CONF_UNIT_OF_MEASUREMENT): str,
            vol.Optional(CONF_MODE, default="slider"): vol.In(["box", "slider"]),
        }
    )


@SELECTORS.register("boolean")
class BooleanSelector(Selector):
    """Selector of a boolean value."""

    CONFIG_SCHEMA = vol.Schema({})


@SELECTORS.register("datetime")
class DateTimeSelector(Selector):
    """Selector of a date and or time value."""

    CONFIG_SCHEMA = vol.Schema(
        {
            vol.Optional("has_date", default=False): bool,
            vol.Optional("has_time", default=False): bool,
        }
    )
