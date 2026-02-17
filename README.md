# Smart-Study-Area-IoT-Dashboard
A real-time IoT-based climate monitoring system that collects temperature and humidity data using an ESP32 + DHT22 sensor, transmits it via MQTT, and visualizes it through an interactive Dash + Plotly web dashboard.

This project demonstrates end-to-end integration of IoT hardware, real-time data streaming, and data visualization engineering

---
### 🚀 Project Overview

This system continuously monitors environmental conditions in a study area and provides live analytics through a professional dashboard.

#### Data Flow Architecture
```text

DHT22 Sensor 
      ↓
ESP32 Microcontroller 
      ↓ (WiFi)
MQTT Broker (test.mosquitto.org)
      ↓
Python Dash Dashboard
      ↓
Interactive Visual Analytics
````
### Key Features

#### 📡 IoT Layer

- ESP32 microcontroller

- DHT22 temperature & humidity sensor

- WiFi connectivity

- Real-time MQTT publishing

- Auto-reconnection handling

#### 📊 Dashboard Layer (Dash + Plotly)

- Live-updating gauges (Temperature & Humidity)

- Real-time time-series line charts

- Correlation heatmap analysis

- Statistical summary (min, max, average)

- Professional UI using Dash Bootstrap Components

- MQTT connection status indicator

- Automatic data buffering

----
### 🛠 Technologies Used
##### Hardware

- ESP32

- DHT22 Sensor

##### Communication

- MQTT Protocol

- test.mosquitto.org Public Broker

##### Software

- Python 3.x

- Dash

- Plotly

- Pandas

- Paho-MQTT

- Dash Bootstrap Components

----
### 📊 Dashboard Preview

<img width="1919" height="893" alt="Dashboard_UI_" src="https://github.com/user-attachments/assets/bcc4dc70-a13a-48e1-8d8f-04951aef989a" />

---- 
### How to Run the Dashboard
#### 1) Clone the repository
```text
git clone https://github.com/YOUR_USERNAME/Smart-Study-Area-IoT-Dashboard.git
cd Smart-Study-Area-IoT-Dashboard/dashboard
````
#### 2) Install dependencies
```text
pip install -r requirements.txt
````
#### 3) Run the dashboard
```text
python live-dashboard.py
````
----
### MQTT Configuration
```text
Broker: test.mosquitto.org
Port: 1883
Topic: jtown/study_area/data
````
Note: This project uses a public MQTT broker for demonstration purposes

----
### 📁 Project Structure

----

### 📈 Analytical Capabilities

- Real-time environmental trend monitoring

- Correlation analysis between temperature and humidity

- Dynamic axis scaling

- Floating precision control (e.g., 28.85°C, 80.45%)

- 15-second time tick intervals

- Automated buffer management

----
### 🧠 Learning Outcomes

This project demonstrates knowledge in:

- IoT system design

- MQTT protocol implementation

- Real-time data engineering

- Python dashboard development

- Data visualization best practices

- Embedded systems programming

- Network communication debugging

----
### Security Note
* Sensitive credentials (WiFi passwords) are excluded from this repository.

----
#### 👨‍💻 Author
Jonathan Mishayel | Data Science Student
@ 2025


