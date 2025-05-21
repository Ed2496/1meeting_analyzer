"""
會議資料結構設計
用於解析 Teams 會議字幕文字檔，並自動彙整會議紀錄與工作事項
"""

class MeetingRecord:
    """會議記錄的主要資料結構"""
    
    def __init__(self):
        # 會議基本資訊
        self.title = ""  # 會議標題
        self.date = ""   # 會議日期
        self.time = ""   # 會議時間
        self.participants = []  # 參與人員列表
        
        # 會議內容
        self.topics = []  # 議題列表，每個議題是一個 Topic 物件
        
        # 工作事項追蹤
        self.action_items = []  # 工作事項列表，每個工作事項是一個 ActionItem 物件
        
        # 效率分析
        self.previous_meeting = None  # 前次會議記錄，用於效率分析
        self.efficiency_metrics = {}  # 效率指標，如完成率、延遲率等
    
    def to_dict(self):
        """將會議記錄轉換為字典格式，方便 JSON 序列化"""
        return {
            "title": self.title,
            "date": self.date,
            "time": self.time,
            "participants": self.participants,
            "topics": [topic.to_dict() for topic in self.topics],
            "action_items": [item.to_dict() for item in self.action_items],
            "efficiency_metrics": self.efficiency_metrics
        }
    
    @classmethod
    def from_dict(cls, data):
        """從字典格式建立會議記錄物件"""
        meeting = cls()
        meeting.title = data.get("title", "")
        meeting.date = data.get("date", "")
        meeting.time = data.get("time", "")
        meeting.participants = data.get("participants", [])
        
        # 建立議題物件
        for topic_data in data.get("topics", []):
            topic = Topic.from_dict(topic_data)
            meeting.topics.append(topic)
        
        # 建立工作事項物件
        for item_data in data.get("action_items", []):
            item = ActionItem.from_dict(item_data)
            meeting.action_items.append(item)
        
        meeting.efficiency_metrics = data.get("efficiency_metrics", {})
        
        return meeting


class Topic:
    """會議議題的資料結構"""
    
    def __init__(self):
        self.id = ""  # 議題編號，如 "1"、"2" 等
        self.title = ""  # 議題標題
        self.description = ""  # 議題描述
        self.discussion_points = []  # 討論要點列表
        self.decisions = []  # 決策列表
        self.related_action_items = []  # 相關工作事項的 ID 列表
    
    def to_dict(self):
        """將議題轉換為字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "discussion_points": self.discussion_points,
            "decisions": self.decisions,
            "related_action_items": self.related_action_items
        }
    
    @classmethod
    def from_dict(cls, data):
        """從字典格式建立議題物件"""
        topic = cls()
        topic.id = data.get("id", "")
        topic.title = data.get("title", "")
        topic.description = data.get("description", "")
        topic.discussion_points = data.get("discussion_points", [])
        topic.decisions = data.get("decisions", [])
        topic.related_action_items = data.get("related_action_items", [])
        
        return topic


class ActionItem:
    """工作事項的資料結構"""
    
    def __init__(self):
        self.id = ""  # 工作事項 ID，用於追蹤
        self.description = ""  # 工作事項描述
        self.assignee = ""  # 負責人
        self.due_date = ""  # 截止日期
        self.status = ""  # 狀態：pending（待處理）、in_progress（進行中）、completed（已完成）、delayed（延遲）
        self.related_topic_id = ""  # 相關議題 ID
        self.completion_date = ""  # 完成日期
        self.notes = ""  # 備註
    
    def to_dict(self):
        """將工作事項轉換為字典格式"""
        return {
            "id": self.id,
            "description": self.description,
            "assignee": self.assignee,
            "due_date": self.due_date,
            "status": self.status,
            "related_topic_id": self.related_topic_id,
            "completion_date": self.completion_date,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """從字典格式建立工作事項物件"""
        item = cls()
        item.id = data.get("id", "")
        item.description = data.get("description", "")
        item.assignee = data.get("assignee", "")
        item.due_date = data.get("due_date", "")
        item.status = data.get("status", "")
        item.related_topic_id = data.get("related_topic_id", "")
        item.completion_date = data.get("completion_date", "")
        item.notes = data.get("notes", "")
        
        return item


class EfficiencyAnalyzer:
    """會議效率分析器"""
    
    @staticmethod
    def analyze(current_meeting, previous_meeting=None):
        """分析會議效率，比較當前會議與前次會議"""
        metrics = {}
        
        # 計算當前會議的工作事項完成率
        total_items = len(current_meeting.action_items)
        completed_items = sum(1 for item in current_meeting.action_items if item.status == "completed")
        completion_rate = (completed_items / total_items) * 100 if total_items > 0 else 0
        metrics["current_completion_rate"] = completion_rate
        
        # 如果有前次會議記錄，進行比較分析
        if previous_meeting:
            # 計算前次會議的工作事項完成率
            prev_total_items = len(previous_meeting.action_items)
            prev_completed_items = sum(1 for item in previous_meeting.action_items if item.status == "completed")
            prev_completion_rate = (prev_completed_items / prev_total_items) * 100 if prev_total_items > 0 else 0
            metrics["previous_completion_rate"] = prev_completion_rate
            
            # 計算完成率變化
            metrics["completion_rate_change"] = completion_rate - prev_completion_rate
            
            # 計算延遲率變化
            current_delayed_items = sum(1 for item in current_meeting.action_items if item.status == "delayed")
            current_delay_rate = (current_delayed_items / total_items) * 100 if total_items > 0 else 0
            
            prev_delayed_items = sum(1 for item in previous_meeting.action_items if item.status == "delayed")
            prev_delay_rate = (prev_delayed_items / prev_total_items) * 100 if prev_total_items > 0 else 0
            
            metrics["current_delay_rate"] = current_delay_rate
            metrics["previous_delay_rate"] = prev_delay_rate
            metrics["delay_rate_change"] = current_delay_rate - prev_delay_rate
            
            # 分析重複議題
            current_topics = set(topic.title for topic in current_meeting.topics)
            previous_topics = set(topic.title for topic in previous_meeting.topics)
            repeated_topics = current_topics.intersection(previous_topics)
            
            metrics["repeated_topics_count"] = len(repeated_topics)
            metrics["repeated_topics_percentage"] = (len(repeated_topics) / len(current_topics)) * 100 if current_topics else 0
            metrics["repeated_topics"] = list(repeated_topics)
        
        return metrics


class MeetingParser:
    """會議記錄解析器，用於從文字檔中提取會議資訊"""
    
    @staticmethod
    def parse_text_file(file_content):
        """解析文字檔內容，建立會議記錄物件"""
        meeting = MeetingRecord()
        
        # 解析會議標題
        title_match = MeetingParser._extract_title(file_content)
        if title_match:
            meeting.title = title_match
        
        # 解析會議時間
        date_match, time_match = MeetingParser._extract_datetime(file_content)
        if date_match:
            meeting.date = date_match
        if time_match:
            meeting.time = time_match
        
        # 解析參與人員
        participants = MeetingParser._extract_participants(file_content)
        meeting.participants = participants
        
        # 解析議題
        topics = MeetingParser._extract_topics(file_content)
        meeting.topics = topics
        
        # 解析工作事項
        action_items = MeetingParser._extract_action_items(file_content)
        meeting.action_items = action_items
        
        return meeting
    
    @staticmethod
    def _extract_title(content):
        """從內容中提取會議標題"""
        import re
        
        # 嘗試匹配標題模式
        title_patterns = [
            r"(.*?)(會議|評審會議|工程會議|週會).*?紀錄",
            r"Subject:.*?([^\n]+)"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0).strip()
        
        return ""
    
    @staticmethod
    def _extract_datetime(content):
        """從內容中提取會議日期和時間"""
        import re
        
        # 嘗試匹配日期模式
        date_patterns = [
            r"會議時間[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{4}[-/]\d{1,2}[-/]\d{1,2})",
            r"(\d{4}年\d{1,2}月\d{1,2}日|\d{4}[-/]\d{1,2}[-/]\d{1,2})"
        ]
        
        date_match = None
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                date_match = match.group(1).strip()
                break
        
        # 嘗試匹配時間模式
        time_patterns = [
            r"(\d{1,2}[:：]\d{2})",
            r"會議時間[：:]\s*.*?(\d{1,2}[:：]\d{2})"
        ]
        
        time_match = None
        for pattern in time_patterns:
            match = re.search(pattern, content)
            if match:
                time_match = match.group(1).strip()
                break
        
        return date_match, time_match
    
    @staticmethod
    def _extract_participants(content):
        """從內容中提取參與人員"""
        import re
        
        # 嘗試匹配參與人員模式
        participants_patterns = [
            r"參[與加]人員[：:]\s*(.*?)(?=\n|$)",
            r"To:.*?([^\n]+)"
        ]
        
        participants = []
        for pattern in participants_patterns:
            match = re.search(pattern, content)
            if match:
                participants_text = match.group(1).strip()
                # 分割參與人員列表
                participants = re.split(r'[,，、；;]', participants_text)
                participants = [p.strip() for p in participants if p.strip()]
                break
        
        return participants
    
    @staticmethod
    def _extract_topics(content):
        """從內容中提取議題"""
        import re
        
        topics = []
        
        # 嘗試匹配議題模式
        topic_patterns = [
            r"(\d+)\.\s+(.*?)(?=\n\s*\d+\.\s+|\Z)",
            r"\*(\d+)\.\s+(.*?)(?=\*\d+\.\s+|\Z)"
        ]
        
        for pattern in topic_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                topic = Topic()
                topic.id = match.group(1).strip()
                
                # 提取議題標題和描述
                topic_content = match.group(2).strip()
                title_end = topic_content.find("\n")
                if title_end > 0:
                    topic.title = topic_content[:title_end].strip()
                    topic.description = topic_content[title_end:].strip()
                else:
                    topic.title = topic_content
                
                # 提取討論要點
                discussion_points = MeetingParser._extract_discussion_points(topic_content)
                topic.discussion_points = discussion_points
                
                # 提取決策
                decisions = MeetingParser._extract_decisions(topic_content)
                topic.decisions = decisions
                
                topics.append(topic)
        
        return topics
    
    @staticmethod
    def _extract_discussion_points(topic_content):
        """從議題內容中提取討論要點"""
        import re
        
        discussion_points = []
        
        # 嘗試匹配討論要點模式
        point_patterns = [
            r"[-•*]\s*(.*?)(?=\n[-•*]|\Z)",
            r"(\d+)\)\s+(.*?)(?=\n\d+\)|\Z)"
        ]
        
        for pattern in point_patterns:
            matches = re.finditer(pattern, topic_content, re.DOTALL)
            for match in matches:
                point = match.group(1).strip()
                if point:
                    discussion_points.append(point)
        
        return discussion_points
    
    @staticmethod
    def _extract_decisions(topic_content):
        """從議題內容中提取決策"""
        import re
        
        decisions = []
        
        # 嘗試匹配決策模式
        decision_patterns = [
            r"決[策定][：:]\s*(.*?)(?=\n|$)",
            r"結論[：:]\s*(.*?)(?=\n|$)"
        ]
        
        for pattern in decision_patterns:
            matches = re.finditer(pattern, topic_content, re.DOTALL)
            for match in matches:
                decision = match.group(1).strip()
                if decision:
                    decisions.append(decision)
        
        return decisions
    
    @staticmethod
    def _extract_action_items(content):
        """從內容中提取工作事項"""
        import re
        
        action_items = []
        
        # 嘗試匹配工作事項區塊
        action_block_patterns = [
            r"工作事項[：:](.*?)(?=\n\n|\Z)",
            r"本次會議待辦事項(.*?)(?=\n\n|\Z)"
        ]
        
        action_blocks = []
        for pattern in action_block_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                action_blocks.append(match.group(1).strip())
        
        # 如果找到工作事項區塊，解析其中的工作事項
        if action_blocks:
            for block in action_blocks:
                # 嘗試匹配工作事項模式
                item_patterns = [
                    r"[*•-]\s*(.*?)(?=\n[*•-]|\Z)",
                    r"(\d+)\.\s+(.*?)(?=\n\d+\.|\Z)"
                ]
                
                for pattern in item_patterns:
                    matches = re.finditer(pattern, block, re.DOTALL)
                    for i, match in enumerate(matches):
                        item = ActionItem()
                        item.id = f"AI{len(action_items) + 1}"
                        item.description = match.group(1).strip()
                        
                        # 提取負責人
                        assignee_match = re.search(r"負責人[：:]\s*(.*?)(?=\n|$)", item.description)
                        if assignee_match:
                            item.assignee = assignee_match.group(1).strip()
                        
                        # 提取截止日期
                        due_date_match = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2})[前完成]*", item.description)
                        if due_date_match:
                            item.due_date = due_date_match.group(1).strip()
                        
                        # 提取狀態
                        if re.search(r"(已完成|完成|已處理)", item.description):
                            item.status = "completed"
                        elif re.search(r"(進行中|處理中)", item.description):
                            item.status = "in_progress"
                        elif re.search(r"(延遲|延期|待處理)", item.description):
                            item.status = "delayed"
                        else:
                            item.status = "pending"
                        
                        action_items.append(item)
        
        # 如果沒有找到明確的工作事項區塊，嘗試從整個內容中提取
        if not action_items:
            # 嘗試匹配可能的工作事項模式
            potential_patterns = [
                r"([A-Za-z\u4e00-\u9fa5]+)\s*[:：]\s*(.*?)(?=\n\n|\Z)",
                r"負責人[：:]\s*([A-Za-z\u4e00-\u9fa5]+).*?(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2})[前完成]*"
            ]
            
            for pattern in potential_patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for i, match in enumerate(matches):
                    item = ActionItem()
                    item.id = f"AI{len(action_items) + 1}"
                    
                    if len(match.groups()) >= 2:
                        item.assignee = match.group(1).strip()
                        item.description = match.group(2).strip()
                    else:
                        item.description = match.group(0).strip()
                    
                    # 提取截止日期
                    due_date_match = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2})[前完成]*", item.description)
                    if due_date_match:
                        item.due_date = due_date_match.group(1).strip()
                    
                    # 提取狀態
                    if re.search(r"(已完成|完成|已處理)", item.description):
                        item.status = "completed"
                    elif re.search(r"(進行中|處理中)", item.description):
                        item.status = "in_progress"
                    elif re.search(r"(延遲|延期|待處理)", item.description):
                        item.status = "delayed"
                    else:
                        item.status = "pending"
                    
                    action_items.append(item)
        
        return action_items
