#!/usr/bin/env python3
"""
Real-time EM Tracker streaming for catheter control

Usage:
    python em_tracker_realtime.py                         # Stream CSV to console
    python em_tracker_realtime.py --output data.csv       # Save CSV to file
    python em_tracker_realtime.py --format json           # Stream JSON
    python em_tracker_realtime.py --format json -o data.jsonl  # Save JSON
"""

import sys
import time
import json
import argparse

if not sys.platform.startswith('win'):
    print("ERROR: TrakStar EM tracker only works on Windows")
    sys.exit(1)

try:
    from pytrak.trakstar import TrakSTARInterface
except ImportError:
    print("ERROR: Could not import pytrak")
    sys.exit(1)


class EMTrackerStreamer:
    
    def __init__(self):
        self.interface = TrakSTARInterface()
        self.start_time = None
        
    def connect(self):
        print("Initializing TrakStar EM tracker...", file=sys.stderr)
        
        try:
            self.interface.initialize()
        except Exception as e:
            print(f"ERROR: Failed to initialize tracker: {e}", file=sys.stderr)
            return False
        
        self.start_time = time.time()
        print("EM Tracker ready!", file=sys.stderr)
        print(f"Attached sensors: {self.interface.attached_sensors}", file=sys.stderr)
        return True
    
    def disconnect(self):

        if self.interface:
            print("\nClosing tracker connection...", file=sys.stderr)
            self.interface.close()
    
    def get_data(self):
        """Get current sensor data"""
        if not self.interface or not self.interface.is_init:
            return None
        
        try:
            return self.interface.get_synchronous_data_dict(write_data_file=False)
        except Exception as e:
            print(f"ERROR reading data: {e}", file=sys.stderr)
            return None


def stream_csv(streamer, output_file=None):
    """Stream data in CSV format"""
    
    file_handle = None
    if output_file:
        file_handle = open(output_file, 'w')
        print(f"Recording to: {output_file}", file=sys.stderr)
    
    # Write CSV header
    header = "timestamp_ms,sensor_id,x,y,z,azimuth,elevation,roll,quality"
    print(header)
    if file_handle:
        file_handle.write(header + '\n')
    
    print("Streaming CSV data... Press Ctrl+C to stop", file=sys.stderr)
    
    try:
        sample_count = 0
        while True:
            data = streamer.get_data()
            if data and 'time' in data:
                timestamp = data['time']
                
                for sensor_id in streamer.interface.attached_sensors:
                    if sensor_id in data:
                        s = data[sensor_id]
                        csv_line = (f"{timestamp},{sensor_id},"
                                   f"{s[0]:.4f},{s[1]:.4f},{s[2]:.4f},"
                                   f"{s[3]:.4f},{s[4]:.4f},{s[5]:.4f},"
                                   f"{int(s[6])}")
                        
                        print(csv_line)
                        if file_handle:
                            file_handle.write(csv_line + '\n')
                
                if file_handle:
                    file_handle.flush()
                
                sample_count += 1
                if sample_count % 100 == 0:
                    print(f"# Samples: {sample_count}", file=sys.stderr)
            
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        print("\n\nStopping...", file=sys.stderr)
    finally:
        if file_handle:
            file_handle.close()
            print(f"Saved {sample_count} samples to {output_file}", file=sys.stderr)


def stream_json(streamer, output_file=None):
    """Stream data in compact JSON format (one object per line)"""
    
    file_handle = None
    if output_file:
        file_handle = open(output_file, 'w')
        print(f"Recording to: {output_file}", file=sys.stderr)
    
    print("Streaming JSON data... Press Ctrl+C to stop", file=sys.stderr)
    
    try:
        sample_count = 0
        while True:
            data = streamer.get_data()
            if data and 'time' in data:
                timestamp = data['time']
                
                # Build compact JSON object
                json_obj = {"t": timestamp, "sensors": {}}
                
                for sensor_id in streamer.interface.attached_sensors:
                    if sensor_id in data:
                        s = data[sensor_id]
                        json_obj["sensors"][sensor_id] = {
                            "pos": [round(s[0], 4), round(s[1], 4), round(s[2], 4)],
                            "ori": [round(s[3], 4), round(s[4], 4), round(s[5], 4)],
                            "q": int(s[6])
                        }
                
                json_line = json.dumps(json_obj)
                print(json_line)
                
                if file_handle:
                    file_handle.write(json_line + '\n')
                    file_handle.flush()
                
                sample_count += 1
                if sample_count % 100 == 0:
                    print(f"# Samples: {sample_count}", file=sys.stderr)
            
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        print("\n\nStopping...", file=sys.stderr)
    finally:
        if file_handle:
            file_handle.close()
            print(f"Saved {sample_count} samples to {output_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Stream real-time EM tracker data')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Output file to save data (optional)')
    parser.add_argument('--format', '-f', type=str, default='csv',
                       choices=['csv', 'json'],
                       help='Output format: csv or json (default: csv)')
    args = parser.parse_args()
    
    streamer = EMTrackerStreamer()
    
    if not streamer.connect():
        print("Failed to connect to EM tracker.", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.format == 'json':
            stream_json(streamer, args.output)
        else:
            stream_csv(streamer, args.output)
    finally:
        streamer.disconnect()


if __name__ == '__main__':
    main()

