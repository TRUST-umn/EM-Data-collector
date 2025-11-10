# EM-Data-collector

## Quick Start

### 1. Requirements

- Windows OS 
- TrakStar hardware connected and powered on
- Python 3.6+
- Install drivers from https://drive.google.com/drive/folders/1Gusb3T4gf5J67fZ-n6SzZM5O2ATfuEda?usp=sharing (download the whole "10006809" folder and run install.msi)

### 2. Install

```bash
pip install numpy
```

### 3. Run

**Stream CSV to console:**
```bash
python em_tracker_realtime.py
```

**Stream JSON:**
```bash
python em_tracker_realtime.py --format json
```

**Record to file:**
```bash
python em_tracker_realtime.py --output experiment.csv
python em_tracker_realtime.py --format json --output data.jsonl
```

## Data Formats

### CSV Format

Simple tabular format:

```csv
timestamp_ms,sensor_id,x,y,z,azimuth,elevation,roll,quality
1234567,1,12.3456,-23.4567,145.6789,45.1234,12.4567,-5.7890,0
```

**Columns:**
- `timestamp_ms`: Tracker system time in milliseconds
- `sensor_id`: Sensor ID (1-4)
- `x, y, z`: Position in millimeters
- `azimuth, elevation, roll`: Orientation in degrees (Euler angles)
- `quality`: Signal quality (0 = good)

### JSON Format 

Compact JSON Lines format (one object per line):

```json
{"t":1234567,"sensors":{"1":{"pos":[12.3456,-23.4567,145.6789],"ori":[45.1234,12.4567,-5.7890],"q":0}}}
```

**Fields:**
- `t`: Timestamp in milliseconds
- `sensors`: Dictionary of sensor data by ID
  - `pos`: [x, y, z] position in millimeters
  - `ori`: [azimuth, elevation, roll] in degrees
  - `q`: Quality (0 = good)

