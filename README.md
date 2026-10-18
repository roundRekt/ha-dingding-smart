# 叮叮智能 - Home Assistant 集成

基于逆向的Python推送实现的Home Assistant自定义集成，支持叮叮智能门铃/摄像头的开门事件监控、远程开锁等功能。

## 功能特性

- ✅ 门锁设备映射（原生支持 HA `lock` 平台，开锁状态联动，5秒自动上锁）
- ✅ 设备与实体归入（支持 HA 设备注册表，将门锁、传感器、二进制传感器归入统一设备）
- ✅ 实时推送监听（基于SSL/TLS）
- ✅ 开门事件监控（指纹、密码、门内开锁）
- ✅ 门铃呼叫通知
- ✅ 设备在线/离线状态
- ✅ 多种报警事件（PIR移动侦测、低电量、温度报警等）
- ✅ 门锁状态传感器（自动5秒恢复）
- ✅ 完全脱离Android系统运行
- ✅ Token持久化存储
- ✅ 线程安全的事件处理

## GitHub仓库

📦 **GitHub地址**: https://github.com/roundRekt/ha-dingding-smart

## 安装指南

### 方法 1：通过 HACS 自定义存储库安装（推荐）

本集成支持通过 HACS（Home Assistant Community Store）添加自定义存储库安装，后续可直接在 HACS 内一键更新：

1. 打开 Home Assistant，在左侧边栏点击 **HACS**
2. 点击右上角 **三个点 (⋮)** 菜单，选择 **自定义存储库**（Custom repositories）
3. 在弹出的窗口中填入：
   - **存储库**：`https://github.com/roundRekt/ha-dingding-smart`
   - **类别**：选择 **集成**（Integration）
4. 点击 **添加**（Add），等待添加完成
5. 在 HACS 集成列表中搜索并进入 **叮叮智能**，点击右下角 **下载**（Download）
6. 下载完成后，**重启 Home Assistant**

---

### 方法 2：手动安装（备用）

如果不使用 HACS，也可以直接手动部署：

1. 下载或克隆本仓库代码
2. 将 `custom_components/dingding_smart` 文件夹复制到你的 Home Assistant 配置目录的 `custom_components/` 目录下：
   ```bash
   # 默认配置目录
   cp -r custom_components/dingding_smart ~/.homeassistant/custom_components/

   # 对于 Docker 安装环境
   cp -r custom_components/dingding_smart /path/to/your/homeassistant/config/custom_components/

   # 对于 Home Assistant OS
   # 通过 Samba、FTP 或 SSH 传输到 /config/custom_components/ 目录下
   ```
3. 重启 Home Assistant

---

### 添加集成与配置

重启完成后，即可在 Home Assistant 界面中添加设备：

1. 打开 Home Assistant，进入 **设置** → **设备与服务**
2. 点击右下角 **添加集成**
3. 搜索 **叮叮智能**（或 `dingding`）并点击
4. 在配置界面填写账号信息：
   - **用户名/手机号**：叮叮智能 App 的登录账号（手机号）
   - **密码**：叮叮智能 App 登录密码
   - **服务器区域**：选择账号所在的服务器区域（中国 / 欧洲 / 美国）
5. 点击 **提交**，系统将自动验证登录并自动发现加载所有门锁与传感器设备

## 配置

### 基本配置

| 字段 | 说明 | 示例 |
|------|------|------|
| 用户名 | 叮叮智能App的登录账号 | `13800138000` |
| 密码 | 叮叮智能App的登录密码 | `your_password` |
| 服务器区域 | 选择服务器所在区域 | `中国` / `欧洲` / `美国` |

### 可选配置

在 `configuration.yaml` 中添加以下可选配置：

```yaml
dingding_smart:
  username: 13800138000
  password: your_password
  server_region: cn  # cn, eu, us
  device_uid: "your_device_uid"  # 可选：只监听指定设备
  user_id: 12742576  # 可选：用户ID
  imei: "your_imei"  # 可选：设备IMEI号，用于推送绑定
```

## 实体与设备归入

本集成支持 Home Assistant 设备注册表（Device Registry），会将每个门锁设备的门锁实体、传感器、二进制传感器统一归入到同一个设备卡片下。

### 门锁实体 (Lock)

| 实体ID | 名称 | 说明 |
|---------|------|------|
| `lock.{device_name}_lock` | 门锁 | 原生门锁实体。平时为已锁定状态；检测到开门事件后自动切换为开锁状态，并在 5 秒后自动恢复为已锁定。支持在 HA 中手动锁定。 |

### 传感器实体 (Sensor)

集成会为每个设备创建以下传感器：

| 实体ID | 名称 | 说明 |
|---------|------|------|
| `sensor.{device_name}_battery` | 电池电量 | 设备电池电量百分比 |
| `sensor.{device_name}_wifi_signal` | WiFi信号 | 设备WiFi信号强度 |
| `sensor.{device_name}_status` | 设备状态 | 设备当前状态 |
| `sensor.{device_name}_last_unlock` | 最后开锁 | 最后一次开锁事件信息 |
| `sensor.{device_name}_online` | 在线状态 | 设备在线状态布尔值 |
| `sensor.{device_name}_version` | 固件版本 | 设备固件版本信息 |
| `sensor.{device_name}_uid` | 设备UID | 设备唯一标识符 |
| `sensor.{device_name}_online_type` | 在线类型 | 连接类型（WiFi/有线/4G） |
| `sensor.{device_name}_update_time` | 最后更新 | 设备最后更新时间 |

### 二进制传感器实体 (Binary Sensor)

| 实体ID | 名称 | 说明 |
|---------|------|------|
| `binary_sensor.{device_name}_door_lock` | 门内开锁状态 | 门内开锁状态（5秒自动恢复） |
| `binary_sensor.{device_name}_outside_door_unlock` | 门外开锁状态 | 门外开锁状态（5秒自动恢复） |

## 事件

集成会触发以下Home Assistant事件：

### 开门事件

**事件名**: `dingding_smart_door_unlock`

**数据**:
```json
{
  "uid": "device_uid",
  "method": "fingerprint|password|inside_lock",
  "message": "开门消息",
  "alert": "提示信息",
  "name": "设备名称"
}
```

**开锁方法**:
- `fingerprint`: 指纹开锁
- `password`: 密码开锁
- `inside_lock`: 门内开锁

### 门铃呼叫事件

**事件名**: `dingding_smart_door_call`

**数据**:
```json
{
  "uid": "device_uid",
  "message": "呼叫消息",
  "alert": "提示信息",
  "name": "设备名称"
}
```

### 设备离线事件

**事件名**: `dingding_smart_door_offline`

**数据**:
```json
{
  "uid": "device_uid",
  "message": "离线消息",
  "alert": "提示信息",
  "name": "设备名称"
}
```

### 设备上线事件

**事件名**: `dingding_smart_door_online`

**数据**:
```json
{
  "uid": "device_uid",
  "message": "上线消息",
  "alert": "提示信息",
  "name": "设备名称"
}
```

### 报警事件

**事件名**: `dingding_smart_alarm`

**数据**:
```json
{
  "uid": "device_uid",
  "type": "0|4|8|9|10",
  "message": "报警消息",
  "alert": "提示信息",
  "name": "设备名称"
}
```

**报警类型**:
- `0`: PIR移动侦测
- `4`: 低电量
- `8`: 低温报警
- `9`: 高温报警
- `10`: 声音报警

## 自动化示例

### 1. 开门时发送通知

```yaml
automation:
  - alias: "门铃开门通知"
    trigger:
      - platform: event
        event_type: dingding_smart_door_unlock
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "门铃开门通知"
          message: "检测到开门事件！方式: {{ trigger.event.data.method }}"
```

### 2. 门内开锁时发送通知

```yaml
automation:
  - alias: "门内开锁提醒"
    trigger:
      - platform: event
        event_type: dingding_smart_door_unlock
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.method == 'inside_lock' }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "门内开锁"
          message: "有人在门内开锁了！"
```

### 3. 门铃呼叫时播放声音

```yaml
automation:
  - alias: "门铃呼叫提醒"
    trigger:
      - platform: event
        event_type: dingding_smart_door_call
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.speaker
        data:
          media_content_id: "doorbell_sound.mp3"
          media_content_type: music
```

### 4. 设备离线时报警

```yaml
automation:
  - alias: "门铃离线报警"
    trigger:
      - platform: event
        event_type: dingding_smart_door_offline
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "门铃离线警告"
          message: "门铃设备 {{ trigger.event.data.name }} 已离线！"
```

### 5. 指纹开锁时记录日志

```yaml
automation:
  - alias: "指纹开锁记录"
    trigger:
      - platform: event
        event_type: dingding_smart_door_unlock
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.method == 'fingerprint' }}"
    action:
      - service: logbook.log
        data:
          name: "门铃"
          message: "指纹开锁 - {{ trigger.event.data.name }}"
```

## 故障排除

### 登录失败

**错误**: `auth_error`

**解决方法**:
- 检查用户名和密码是否正确
- 确认账号可以在叮叮智能App中正常登录
- 检查服务器区域是否选择正确

### 未找到设备

**错误**: `no_devices`

**解决方法**:
- 确认账号下已绑定设备
- 在叮叮智能App中检查设备是否在线
- 尝试重新登录叮叮智能App

### 推送连接失败

**症状**: 无法接收推送消息

**解决方法**:
- 检查网络连接
- 确认推送服务器地址和端口正确
- 查看Home Assistant日志获取详细错误信息
- 尝试使用测试脚本单独测试推送连接

### SSL连接错误

**症状**: `SSL handshake failed`

**解决方法**:
- 检查系统时间是否正确
- 确认防火墙没有阻止SSL连接
- 尝试重启Home Assistant
- 查看日志确认SSL证书验证已禁用

### 门锁状态不更新

**症状**: 门锁状态一直显示开锁

**解决方法**:
- 检查Home Assistant日志是否有错误
- 确认推送服务已连接
- 查看事件日志确认收到开门事件
- 重启Home Assistant

## 技术细节

### 推送协议

- **协议**: SSL/TLS over TCP
- **端口**: 11001
- **消息格式**: 8字节消息头 + JSON数据体
- **字节序**: 小端序
- **心跳超时**: 130秒
- **重连机制**: 自动重连，最大重试次数5次
- **SSL证书**: 已禁用证书验证（兼容性优化）

### 消息头格式

```
[0-3]   命令类型 (CMD) - 4字节，小端序
[4-7]   数据长度 (LENGTH) - 4字节，小端序
```

### 命令类型

| 命令 | 值 | 说明 |
|------|-----|------|
| CMD_HEARTBEAT | 0 | 心跳 |
| CMD_REGISTER | 1 | 注册 |
| CMD_TOKEN | 2 | Token |
| CMD_PUSH | 3 | 推送 |

### 实现原理

1. **认证流程**: 通过模拟叮叮智能App的登录请求获取token
2. **设备发现**: 使用token获取用户绑定的设备列表
3. **推送连接**: 建立SSL/TLS连接到推送服务器
4. **Token绑定**: 将推送Token绑定到API服务器
5. **事件处理**: 解析推送消息并转换为Home Assistant事件
6. **状态同步**: 定期同步设备状态
7. **持久化存储**: Token和配置信息持久化存储

## 开发

### 项目结构

```
homeassistant/
├── custom_components/
│   └── dingding_smart/
│       ├── __init__.py          # 主集成文件
│       ├── binary_sensor.py     # 二进制传感器实体
│       ├── config_flow.py       # 配置流程
│       ├── entity.py            # 基础实体
│       ├── lock.py              # 门锁实体
│       ├── manifest.json        # 集成清单
│       ├── sensor.py            # 传感器实体
│       ├── strings.json         # 本地化字符串模板
│       └── translations/        # 多语言翻译目录
│           ├── zh-Hans.json     # 简体中文
│           └── en.json          # 英文
├── hacs.json                    # HACS 集成配置文件
└── README.md                    # 本文件
```

### 开发环境设置

1. 克隆项目到本地
2. 安装依赖（如果需要）
3. 修改代码后测试
4. 提交Pull Request

### 贡献

欢迎提交Issue和Pull Request！

## 版本历史

### v1.0.25 (2026-10-18)
- ✅ 新增门锁设备映射（支持 HA 原生 Lock 平台）
- ✅ 新增设备注册表支持，将门锁与各个传感器、二进制传感器归入对应设备
- ✅ 优化门锁与传感器定时器资源释放
- ✅ 修复配置界面文本本地化问题

### v1.0.12 (2026-02-25)
- ✅ 优化门锁状态自动恢复时间为5秒
- ✅ 添加中文方法显示

### v1.0.11 (2026-02-25)
- ✅ 调整门锁状态恢复时间为5秒

### v1.0.10 (2026-02-25)
- ✅ 修复推送服务和线程安全问题
- ✅ 新增门锁状态传感器
- ✅ 完全禁用SSL证书验证

### v1.0.9 (2026-02-24)
- ✅ Token持久化存储
- ✅ 优化API请求处理

## 许可证

本项目仅供学习和研究使用。

## 致谢

- 感谢叮叮智能设备的支持
- 基于逆向的Python推送实现
- Home Assistant社区的支持

