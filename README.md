# tankmaster-homeassistant
TankMaster – Home Assistant Integration

Native Home Assistant integration for the RiVöt TankMaster contactless tank monitoring system by UGotToad.com

This integration connects directly to a TankMaster device over your local network and exposes tank levels, probe states, and system status as Home Assistant entities — no cloud, no accounts, no subscriptions.

⸻

✨ Features
	•	📊 Tank level monitoring (computed overall level)
	•	💧 Individual probe level sensors (up to 4 probes)
	•	🔘 Binary sensors for liquid detection at each probe
	•	🔌 External power status
	•	📡 Wi-Fi connectivity status
	•	🧠 Device firmware reporting
	•	🏠 Local-only REST API (no internet required)
	•	⚙️ UI-based setup (no YAML required)
	•	📦 HACS-compatible for easy installation

⸻

📦 Supported Devices
	•	RiVöt TankMaster
	•	External power model (BLE + Wi-Fi)
	•	REST API enabled (default)

⸻

🛠 Installation

Option 1: Install via HACS (Recommended)
	1.	Install HACS if you haven’t already
			👉 https://hacs.xyz/
	2.	In Home Assistant:
		•	Go to HACS → Integrations
		•	Click ⋮ → Custom repositories
		•	Add this repository:  https://github.com/woodchuck1234/tankmaster-homeassistant
		•	Category: Integration
	3.	Search for TankMaster in HACS and install it
	4.	Restart Home Assistant

⸻

Option 2: Manual Installation
	1.	Copy the custom_components/tankmaster folder into:
			/config/custom_components/tankmaster
	2.	Restart Home Assistant

⸻

⚙️ Configuration
	1.	Go to Settings → Devices & Services
	2.	Click Add Integration
	3.	Search for TankMaster
	4.	Enter the IP address of your TankMaster (example: 10.0.0.22)
	5.	Done 🎉

No YAML configuration is required.

⸻

📊 Entities Created

Sensors

Entity	Description
sensor.tankmaster_level	Computed overall tank level (%)
sensor.tankmaster_probe_1	Probe 1 level (%)
sensor.tankmaster_probe_2	Probe 2 level (%)
sensor.tankmaster_probe_3	Probe 3 level (%)
sensor.tankmaster_probe_4	Probe 4 level (%)
sensor.tankmaster_firmware	Firmware version

Binary Sensors

Entity	Description
binary_sensor.tankmaster_probe_1_liquid_detected	Liquid detected at probe 1
binary_sensor.tankmaster_probe_2_liquid_detected	Liquid detected at probe 2
binary_sensor.tankmaster_probe_3_liquid_detected	Liquid detected at probe 3
binary_sensor.tankmaster_probe_4_liquid_detected	Liquid detected at probe 4
binary_sensor.tankmaster_external_power	External power present
binary_sensor.tankmaster_wifi_connected	Wi-Fi connected


⸻

📈 Tank Level Logic

TankMaster uses discrete probe thresholds rather than continuous analog sensing.

Typical probe placement:
	•	Probe 1 → ~25%
	•	Probe 2 → ~50%
	•	Probe 3 → ~75%
	•	Probe 4 → ~90%

The Tank Level sensor reports the highest active probe value.

This provides accurate, reliable tank readings without false values caused by residue or fouling.

⸻

🧩 Dashboard Tips
	•	Use a Gauge Card for the overall tank level
	•	Use Binary Sensor badges for probe liquid detection
	•	Group all TankMaster entities under a dedicated dashboard or RV area

A custom TankMaster dashboard card is planned for a future release.

⸻

🛜 Networking Notes
	•	TankMaster must be reachable on your local network
	•	REST API must be enabled (default)
	•	No internet connection required
	•	Works on RV, marine, and off-grid networks

⸻

🧪 Troubleshooting

Integration not found?
	•	Restart Home Assistant
	•	Confirm the integration is installed via HACS

Device shows unavailable?
	•	Verify the TankMaster IP address
	•	Check that the TankMaster web UI loads in your browser

⸻

📄 License

MIT License

⸻

🐸 About RiVöt / UGotToad

TankMaster is designed and built by RiVöt — practical, reliable tech for RV and marine life.

🌐 https://UGotToad.com

⸻

🚧 Roadmap
	•	Custom Lovelace TankMaster gauge card
	•	Auto-discovery via mDNS
	•	MQTT push updates (optional)
	•	Multi-tank dashboards

⸻

If you want, next I can:
	•	Tighten this for HA forum posting
	•	Write a short HACS blurb
	•	Add screenshots / badges
	•	Help you position this for marine users specifically

This README already puts you in the top tier of custom HA integrations.
