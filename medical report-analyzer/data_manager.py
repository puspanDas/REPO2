import sqlite3
import json
import os
from datetime import datetime
import hashlib

class DataManager:
    def __init__(self, db_path='medical_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp TEXT,
                data_type TEXT,
                raw_data TEXT,
                extracted_features TEXT,
                file_path TEXT,
                health_metrics TEXT
            )
        ''')
        
        # Analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_data_id INTEGER,
                analysis_type TEXT,
                results TEXT,
                confidence_score REAL,
                timestamp TEXT,
                FOREIGN KEY (user_data_id) REFERENCES user_data (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_user_data(self, user_id, data_type, raw_data, extracted_features=None, file_path=None, health_metrics=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_data (user_id, timestamp, data_type, raw_data, extracted_features, file_path, health_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            datetime.now().isoformat(),
            data_type,
            raw_data,
            json.dumps(extracted_features) if extracted_features else None,
            file_path,
            json.dumps(health_metrics) if health_metrics else None
        ))
        
        data_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return data_id
    
    def store_analysis_result(self, user_data_id, analysis_type, results, confidence_score=0.0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_results (user_data_id, analysis_type, results, confidence_score, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_data_id,
            analysis_type,
            json.dumps(results),
            confidence_score,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_data(self, user_id, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_data WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
        ''', (user_id, limit))
        
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_all_training_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ud.raw_data, ud.extracted_features, ar.results 
            FROM user_data ud 
            JOIN analysis_results ar ON ud.id = ar.user_data_id
            WHERE ar.analysis_type = 'manual_training'
        ''')
        
        data = cursor.fetchall()
        conn.close()
        return data