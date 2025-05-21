from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import tempfile
import sys
import re
from datetime import datetime

# 添加父目錄到 Python 路徑，以便導入會議資料結構模組
try:
    from meeting_data_structure import MeetingRecord, Topic, ActionItem, MeetingParser, EfficiencyAnalyzer
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from meeting_data_structure import MeetingRecord, Topic, ActionItem, MeetingParser, EfficiencyAnalyzer

app = Flask(__name__)

# 確保上傳目錄存在
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 確保資料儲存目錄存在
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上傳檔案大小為 16MB

# 允許的檔案類型
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    """檢查檔案類型是否允許上傳"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_meeting_record(meeting):
    """儲存會議記錄到 JSON 檔案"""
    # 使用會議日期和標題作為檔案名稱
    date_str = re.sub(r'[^\w]', '_', meeting.date) if meeting.date else datetime.now().strftime('%Y%m%d')
    title_str = re.sub(r'[^\w]', '_', meeting.title)[:30] if meeting.title else 'untitled'
    filename = f"{date_str}_{title_str}.json"
    
    filepath = os.path.join(app.config['DATA_FOLDER'], filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(meeting.to_dict(), f, ensure_ascii=False, indent=2)
    
    return filename

def load_previous_meetings():
    """載入之前的會議記錄"""
    meetings = []
    
    if os.path.exists(app.config['DATA_FOLDER']):
        for filename in os.listdir(app.config['DATA_FOLDER']):
            if filename.endswith('.json'):
                filepath = os.path.join(app.config['DATA_FOLDER'], filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        meeting_data = json.load(f)
                        meeting = MeetingRecord.from_dict(meeting_data)
                        meeting.filename = filename  # 添加檔案名稱屬性，用於前端連結
                        meetings.append(meeting)
                except Exception as e:
                    print(f"Error loading meeting record {filename}: {e}")
    
    # 按日期排序，最新的在前
    meetings.sort(key=lambda m: m.date if m.date else "", reverse=True)
    
    return meetings

@app.route('/')
def index():
    """首頁，顯示上傳表單和之前的會議記錄列表"""
    previous_meetings = load_previous_meetings()
    return render_template('index.html', previous_meetings=previous_meetings)

@app.route('/upload', methods=['POST'])
def upload_file():
    """處理檔案上傳"""
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # 建立臨時檔案
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        
        # 讀取檔案內容
        with open(temp_file.name, 'r', encoding='utf-8', errors='ignore') as f:
            file_content = f.read()
        
        # 解析會議記錄
        meeting = MeetingParser.parse_text_file(file_content)
        
        # 載入之前的會議記錄，用於效率分析
        previous_meetings = load_previous_meetings()
        if previous_meetings:
            # 使用最近的一次會議進行效率分析
            previous_meeting = previous_meetings[0]
            meeting.previous_meeting = previous_meeting
            meeting.efficiency_metrics = EfficiencyAnalyzer.analyze(meeting, previous_meeting)
        
        # 儲存會議記錄
        filename = save_meeting_record(meeting)
        
        # 刪除臨時檔案
        os.unlink(temp_file.name)
        
        # 重定向到會議記錄頁面
        return redirect(url_for('view_meeting', filename=filename))
    
    return redirect(url_for('index'))

@app.route('/meeting/<filename>')
def view_meeting(filename):
    """顯示會議記錄詳情"""
    filepath = os.path.join(app.config['DATA_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return redirect(url_for('index'))
    
    with open(filepath, 'r', encoding='utf-8') as f:
        meeting_data = json.load(f)
        meeting = MeetingRecord.from_dict(meeting_data)
    
    return render_template('meeting.html', meeting=meeting)

@app.route('/api/meetings')
def api_meetings():
    """API 端點，返回所有會議記錄"""
    meetings = load_previous_meetings()
    return jsonify([meeting.to_dict() for meeting in meetings])

@app.route('/api/meeting/<filename>')
def api_meeting(filename):
    """API 端點，返回特定會議記錄"""
    filepath = os.path.join(app.config['DATA_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "Meeting not found"}), 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        meeting_data = json.load(f)
    
    return jsonify(meeting_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
