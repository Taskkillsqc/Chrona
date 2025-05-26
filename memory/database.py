import sqlite3
import json
import os
from datetime import datetime

conn = None

def init_db(path):
    """初始化数据库"""
    global conn
    
    # 确保数据目录存在
    db_dir = os.path.dirname(path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(path, check_same_thread=False)
    c = conn.cursor()
    
    # 创建事件分析表
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE,
        summary TEXT,
        description TEXT,
        start_time TEXT,
        result TEXT,
        reminded INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建提醒记录表
    c.execute('''CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT,
        FOREIGN KEY (event_id) REFERENCES events (id)
    )''')
    
    conn.commit()
    print(f"数据库初始化完成: {path}")

def save_event_analysis(event, result):
    """保存事件分析结果"""
    if not conn:
        print("数据库连接未初始化")
        return False
    
    try:
        c = conn.cursor()
        
        # 使用REPLACE确保同一个事件不会重复插入
        c.execute("""
            INSERT OR REPLACE INTO events 
            (uid, summary, description, start_time, result, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.get('uid', ''),
            event.get('summary', ''),
            event.get('description', ''),
            event.get('start', ''),
            json.dumps(result, ensure_ascii=False),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"保存事件分析失败: {e}")
        return False

def get_events_to_remind():
    """获取需要提醒的事件"""
    if not conn:
        return []
    
    try:
        c = conn.cursor()
        c.execute("""
            SELECT id, uid, summary, description, start_time, result 
            FROM events 
            WHERE reminded = 0 
            AND json_extract(result, '$.need_remind') = 'true'
            ORDER BY start_time
        """)
        
        events = []
        for row in c.fetchall():
            try:
                result = json.loads(row[5])
                events.append({
                    'id': row[0],
                    'uid': row[1],
                    'summary': row[2],
                    'description': row[3],
                    'start_time': row[4],
                    'result': result
                })
            except json.JSONDecodeError:
                continue
                
        return events
        
    except Exception as e:
        print(f"获取待提醒事件失败: {e}")
        return []

def mark_reminded(event_id, status="sent"):
    """标记事件已提醒"""
    if not conn:
        return False
    
    try:
        c = conn.cursor()
        
        # 更新事件状态
        c.execute("UPDATE events SET reminded = 1 WHERE id = ?", (event_id,))
        
        # 记录提醒日志
        c.execute("""
            INSERT INTO reminders (event_id, status) 
            VALUES (?, ?)
        """, (event_id, status))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"标记提醒状态失败: {e}")
        return False

def get_stats():
    """获取统计信息"""
    if not conn:
        return {}
    
    try:
        c = conn.cursor()
        
        # 总事件数
        c.execute("SELECT COUNT(*) FROM events")
        total_events = c.fetchone()[0]
        
        # 需要提醒的事件数
        c.execute("SELECT COUNT(*) FROM events WHERE json_extract(result, '$.need_remind') = 'true'")
        remind_events = c.fetchone()[0]
        
        # 已提醒的事件数
        c.execute("SELECT COUNT(*) FROM events WHERE reminded = 1")
        reminded_events = c.fetchone()[0]
        
        return {
            'total_events': total_events,
            'remind_events': remind_events,
            'reminded_events': reminded_events
        }
        
    except Exception as e:
        print(f"获取统计信息失败: {e}")
        return {}

def cleanup_old_events(days=7):
    """清理旧事件记录"""
    if not conn:
        return False
    
    try:
        c = conn.cursor()
        c.execute("""
            DELETE FROM events 
            WHERE created_at < datetime('now', '-{} days')
        """.format(days))
        
        deleted = c.rowcount
        conn.commit()
        
        if deleted > 0:
            print(f"清理了 {deleted} 条旧事件记录")
        
        return True
        
    except Exception as e:
        print(f"清理旧事件失败: {e}")
        return False
