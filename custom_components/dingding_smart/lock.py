"""叮叮智能 - 门锁实体"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Event, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, DingDingCoordinator, EVENT_DOOR_UNLOCK
from .entity import DingDingEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置门锁实体"""
    coordinator: DingDingCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    devices = coordinator.devices

    entities = []

    for device in devices:
        uid = device.get("uid", "")
        name = device.get("name", f"设备 {uid}")
        entities.append(DingDingLock(coordinator, uid, name))

    if not entities:
        _LOGGER.warning("未找到设备，未创建门锁实体")

    async_add_entities(entities)


class DingDingLock(DingDingEntity, LockEntity):
    """叮叮智能门锁实体"""

    def __init__(self, coordinator: DingDingCoordinator, uid: str, name: str) -> None:
        """初始化门锁实体"""
        super().__init__(coordinator, uid, name)
        self._attr_unique_id = f"{DOMAIN}_{uid}_lock"
        self._attr_name = f"{name} 门锁"
        self._is_locked = True
        self._last_unlock_time: Optional[datetime] = None
        self._last_unlock_method: Optional[str] = None
        self._last_unlock_message: Optional[str] = None
        self._last_unlock_alert: Optional[str] = None
        self._cancel_timer = None

    @property
    def is_locked(self) -> bool:
        """返回门锁是否已锁定"""
        return self._is_locked

    @callback
    def _handle_door_unlock_event(self, event: Event) -> None:
        """处理开门事件"""
        event_uid = event.data.get("uid")
        if event_uid != self._uid:
            return

        method = event.data.get("method", "unknown")
        message = event.data.get("message", "")
        alert = event.data.get("alert", "")

        method_map = {
            "fingerprint": "指纹开锁",
            "password": "密码开锁",
            "inside_lock": "门内开锁",
            "lock": "门锁开锁",
        }
        method_display = method_map.get(method, method)

        _LOGGER.info(
            "门锁 %s 收到开锁事件: method=%s (%s), message=%s, alert=%s",
            self._name,
            method,
            method_display,
            message,
            alert,
        )

        self._is_locked = False
        self._last_unlock_time = datetime.now()
        self._last_unlock_method = method_display
        self._last_unlock_message = message
        self._last_unlock_alert = alert
        self.async_write_ha_state()

        # 取消之前的自动锁定定时器
        if self._cancel_timer:
            self._cancel_timer.cancel()

        # 5秒后自动恢复为已锁定状态
        self._cancel_timer = self.hass.loop.call_later(5, self._auto_lock)

    @callback
    def _auto_lock(self) -> None:
        """自动恢复为已锁定状态"""
        self._is_locked = True
        self._cancel_timer = None
        _LOGGER.info("门锁 %s 状态已自动恢复为已锁定", self._name)
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """处理协调器更新"""
        self.async_write_ha_state()

    async def async_lock(self, **kwargs: Any) -> None:
        """上锁门锁"""
        if self._cancel_timer:
            self._cancel_timer.cancel()
            self._cancel_timer = None
        self._is_locked = True
        _LOGGER.info("门锁 %s 手动设置为已锁定状态", self._name)
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        """开锁门锁"""
        _LOGGER.warning("设备 %s 暂不支持通过云端远程开锁", self._name)
        raise HomeAssistantError(f"{self._name} 暂不支持远程开锁功能")

    async def async_open(self, **kwargs: Any) -> None:
        """打开门锁"""
        await self.async_unlock(**kwargs)

    async def async_added_to_hass(self) -> None:
        """当实体添加到Home Assistant时注册事件监听"""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_DOOR_UNLOCK, self._handle_door_unlock_event)
        )

    async def async_will_remove_from_hass(self) -> None:
        """当实体从Home Assistant移除时清理定时器"""
        if self._cancel_timer:
            self._cancel_timer.cancel()
            self._cancel_timer = None
        await super().async_will_remove_from_hass()

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """获取门锁额外属性"""
        device = self._get_device()
        attrs: Dict[str, Any] = {
            "uid": self._uid,
            "device_id": device.get("id"),
            "battery": device.get("battery"),
            "wifi_signal": device.get("rssi"),
            "current_version": device.get("current_version"),
        }
        if self._last_unlock_time:
            attrs["last_unlock_time"] = self._last_unlock_time.isoformat()
        if self._last_unlock_method:
            attrs["last_unlock_method"] = self._last_unlock_method
        if self._last_unlock_message:
            attrs["last_unlock_message"] = self._last_unlock_message
        if self._last_unlock_alert:
            attrs["last_unlock_alert"] = self._last_unlock_alert
        return attrs
