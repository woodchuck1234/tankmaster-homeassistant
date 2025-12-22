# TankMaster – Home Assistant Integration

Native Home Assistant integration for the **RiVöt TankMaster** contactless RV tank monitoring system.

Monitor your RV’s fresh, gray, and black tanks directly in Home Assistant using local networking — **no cloud, no accounts, no subscriptions required.**

---

## ⚡️ Features

- 🚰 Tank level monitoring (computed %)
- 🔍 Individual probe sensors (up to 4)
- ⚠️ Binary sensors for liquid detection per probe
- 🔌 External power status
- 📶 Wi-Fi connectivity status
- 🧠 Firmware version reporting
- 🌐 Local REST API (no Internet required)
- 🛠 Simple UI-based setup (no YAML needed)
- 🎯 HACS compatible

---

## 📦 Supported Devices

- **RiVöt TankMaster**
- Works anywhere the device is reachable on your local network
- Supports RV, marine, and off-grid installations

---

## 🚀 Installation

### ✅ Option 1 — HACS (Recommended)

1. Ensure **HACS** is installed: https://hacs.xyz
2. In Home Assistant, go to **HACS → Integrations**
3. Click **⋮ → Custom repositories**
4. Add:  https://github.com/woodchuck1234/tankmaster-homeassistant
5. Set category to **Integration**
6. Search for **TankMaster** and install
7. Restart Home Assistant

---

### 📝 Option 2 — Manual Install

1. Copy the folder:  custom_components/tankmaster  into:  /config/custom_components/tankmaster
2. Restart Home Assistant

---

## ⚙️ Configuration

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **TankMaster**
4. Enter your TankMaster device IP (example: `10.0.0.22`)
5. Done! 🎉

No YAML required.

---

## 📊 Entities Created

### 🔢 Sensors

| Entity | Description |
|--------|-------------|
| `sensor.tankmaster_level` | Overall tank % level |
| `sensor.tankmaster_probe_1` | Probe 1 %
| `sensor.tankmaster_probe_2` | Probe 2 %
| `sensor.tankmaster_probe_3` | Probe 3 %
| `sensor.tankmaster_probe_4` | Probe 4 %
| `sensor.tankmaster_firmware` | Firmware version |

### 🔔 Binary Sensors

| Entity | Description |
|--------|-------------|
| `binary_sensor.tankmaster_probe_1_liquid_detected` | Liquid at probe 1 |
| `binary_sensor.tankmaster_probe_2_liquid_detected` | Liquid at probe 2 |
| `binary_sensor.tankmaster_probe_3_liquid_detected` | Liquid at probe 3 |
| `binary_sensor.tankmaster_probe_4_liquid_detected` | Liquid at probe 4 |
| `binary_sensor.tankmaster_external_power` | External power present |
| `binary_sensor.tankmaster_wifi_connected` | Wi-Fi connected |

---

## 🧮 Tank Level Logic

TankMaster uses discrete contactless probe thresholds, typically placed near:

- 25%
- 50%
- 75%
- 90%

The overall tank % is computed based on the highest detected probe to reduce false readings from residue, foam, or debris.

---

## 🛠 Dashboard Tips

- Use a **Gauge Card** for overall level
- Use **Badges** for each probe state
- Create an **RV / Tank** dashboard area
- Custom Lovelace cards planned in upcoming releases

---

## 📡 Networking Notes

- TankMaster must be reachable on your network
- REST API must be enabled (default)
- Works completely offline

---

## ⚠️ Troubleshooting

**Integration not showing?**
- Restart Home Assistant
- Confirm installation via HACS

**Entity unavailable?**
- Verify TankMaster IP
- Open the TankMaster IP in a web browser

---

## 🛣 Roadmap

- 🔍 Automatic discovery via mDNS
- 📡 Optional MQTT push
- 🏕 Multi-tank dashboard grouping
- 🎨 Custom Lovelace gauge card

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🌟 About

RiVöt TankMaster — practical, reliable contactless RV tank monitoring.  
Learn more: https://UGotToad.com
