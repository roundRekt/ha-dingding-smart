"""叮叮智能 - 基础实体"""
import logging
from typing import Any, Dict

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, DingDingCoordinator

_LOGGER = logging.getLogger(__name__)


class DingDingEntity(CoordinatorEntity):
    """叮叮智能实体基类，提供统一的设备信息以将实体归入对应设备"""

    coordinator: DingDingCoordinator

    def __init__(self, coordinator: DingDingCoordinator, uid: str, name: str) -> None:
        """初始化实体基类"""
        super().__init__(coordinator)
        self._uid = uid
        self._device_name = name
        self._name = name

    def _get_device(self) -> Dict[str, Any]:
        """获取当前设备信息字典"""
        for device in self.coordinator.devices:
            if device.get("uid") == self._uid:
                return device
        return {}

    @property
    def device_info(self) -> DeviceInfo:
        """获取设备信息，将属于同一设备的实体归入HA中的对应设备"""
        device = self._get_device()
        model = device.get("product") or "智能门锁"
        sw_version = device.get("current_version")

        return DeviceInfo(
            identifiers={(DOMAIN, self._uid)},
            name=self._device_name,
            manufacturer="叮叮智能",
            model=model,
            sw_version=sw_version,
        )
