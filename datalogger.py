# data_logger.py
import csv
import time
import os

class DataLogger:
    def __init__(self, filename="game_log.csv", fieldnames=None):
        # default columns if you don’t supply your own
        self.fieldnames = fieldnames or [
            "timestamp",   # epoch seconds
            "event",       # e.g. "ability_used", "enemy_killed"
            "phase",       # boss phase or context
            "details"      # JSON-encoded dict of extra info
        ]
        first_write = not os.path.exists(filename)
        self.file = open(filename, "a", newline="")
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        if first_write:
            self.writer.writeheader()

    def log(self, event, phase=None, **kwargs):
        row = {
            "timestamp": time.time(),
            "event":     event,
            "phase":     phase,
            "details":   repr(kwargs)
        }
        self.writer.writerow(row)
        self.file.flush()

    def close(self):
        self.file.close()
