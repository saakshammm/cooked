# local_analyzer.py
# fallback rule-based roaster, now funnier

import re
from datetime import datetime
from collections import defaultdict
import random

NIGHT_START = 23
NIGHT_END = 5

SAVAGE_VERDICTS = [
    "brother stand up. they don't even have you saved as a contact.",
    "this is NOT mutual. this is a hostage situation and you're the hostage.",
    "they text you like a school announcement. cold. formal. zero love.",
    "generational levels of cooked. your bloodline will feel this.",
    "you are carrying harder than prime lebron in the 2016 finals.",
    "this relationship survived entirely on your delusion and 3am anxiety.",
    "the interest graph fell like crypto in 2022. it's over.",
    "one-sided masterclass. harvard should study this level of delusion.",
    "this chat died but nobody told you. you're texting a ghost.",
    "professional level overthinking. this is a w2 job at this point.",
    "you replied before the notification finished vibrating. relax.",
    "they use 😭 as a survival mechanism because words are too hard.",
    "conversation powered by delusion and caffeine. mostly delusion.",
    "you wrote paragraphs. they sent a skull emoji. read the room.",
    "this is the driest chat i have ever seen. sahara desert levels.",
]

BRAINROT_TOKENS = [
    "bro", "bruh", "💀", "😭", "🙏", "no cap", "fr", "ong",
    "based", "cringe", "sus", "yeet", "ratio", "skill issue",
    "goofy", "slay", "ick", "rizz", "gyat", "bet", "sheesh",
    "cap", "bussin", "periodt", "purr", "deadass", "fax", "lowkey",
    "highkey", "nah fr", "its giving", "ate", "left no crumbs"
]

CRASHOUT_PHRASES = [
    "severe crashout detected around {time}. paragraphs were deployed. calls were made. dignity was lost.",
    "found you spiraling at {time}. the double text into triple text into essay combo is studied in labs.",
    "around {time} you decided to send a novel. they replied with 'lol'. crashout confirmed.",
    "crashout behavior spotted at {time}. the rapid fire messages, the tone shift, the regret. all there.",
]

class LocalChatAnalyzer:
    def __init__(self, raw_text, chat_type, user_name=None):
        self.raw = raw_text
        self.chat_type = chat_type
        self.user_name = user_name
        self.messages = []
        self.participants = set()
        self.parse_messages()

    def parse_messages(self):
        lines = self.raw.strip().splitlines()
        pattern = re.compile(
            r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?\s?[APap][Mm])\s*[-–]\s*(.+?):\s*(.+)$'
        )
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = pattern.match(line)
            if not match:
                continue
            date_str = match.group(1)
            time_str = match.group(2).replace('\u202f', ' ')
            sender = match.group(3).strip()
            msg_text = match.group(4).strip()
            skip = ["<Media omitted>", "image omitted", "video omitted", "audio omitted", "sticker omitted"]
            if msg_text in skip:
                continue
            try:
                dt_str = f"{date_str} {time_str}"
                dt = None
                for fmt in [
                    "%m/%d/%y %I:%M %p", "%m/%d/%Y %I:%M %p",
                    "%d/%m/%y %I:%M %p", "%d/%m/%Y %I:%M %p",
                    "%m/%d/%y %I:%M:%S %p", "%m/%d/%Y %I:%M:%S %p"
                ]:
                    try:
                        dt = datetime.strptime(dt_str, fmt)
                        break
                    except ValueError:
                        continue
                if dt is None:
                    continue
                self.messages.append({
                    'timestamp': dt,
                    'sender': sender,
                    'text': msg_text
                })
                self.participants.add(sender)
            except Exception:
                continue
        self.messages.sort(key=lambda x: x['timestamp'])

    def run_analysis(self):
        if not self.messages:
            return {"error": "no valid messages found. check your export."}

        user = self._determine_user()
        stats = self._compute_participant_stats()
        response_stats = self._compute_response_times()
        carrier = self._conversation_carrier(user)
        reply_gap = self._reply_gap_analysis(user, response_stats)
        double_texts = self._count_double_texts(user)
        crashout = self._crashout_detector(user)
        locked_in = self._locked_in_detector(user)
        sleep_damage = self._sleep_schedule_damage()
        brainrot = self._brainrot_analysis()
        aura_loss, aura_reason = self._aura_loss(user, double_texts, response_stats)
        delusion = self._delusion_score(user, stats)
        dry = self._dry_texter_meter(user, stats)
        attachment = self._attachment_imbalance(user, stats)
        verdict = self._pick_savage_verdict(user, delusion, double_texts, crashout, dry, stats)

        return {
            "participants": list(self.participants),
            "user": user,
            "message_count": len(self.messages),
            "stats": {},
            "carrier_percent": carrier,
            "reply_gap": reply_gap,
            "double_texts": double_texts,
            "crashout": crashout,
            "locked_in": locked_in,
            "sleep_damage": sleep_damage,
            "brainrot": brainrot,
            "aura_loss": aura_loss,
            "aura_reason": aura_reason,
            "delusion_score": delusion,
            "dry_texter_meter": dry,
            "attachment_imbalance": attachment,
            "verdict": verdict,
            "group_insights": self._group_insights() if self.chat_type == "group" else None
        }

    def _determine_user(self):
        if self.user_name and self.user_name in self.participants:
            return self.user_name
        if len(self.participants) == 2:
            counts = defaultdict(int)
            for m in self.messages:
                counts[m['sender']] += 1
            return max(counts, key=counts.get)
        return list(self.participants)[0] if self.participants else "unknown"

    def _compute_participant_stats(self):
        stats = defaultdict(lambda: {"message_count": 0, "total_words": 0, "emoji_count": 0, "brainrot_score": 0})
        for m in self.messages:
            s = stats[m['sender']]
            s['message_count'] += 1
            s['total_words'] += len(m['text'].split())
            emojis = re.findall(
                r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
                r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251'
                r'\U0001f926-\U0001f937\U00010000-\U0010ffff\u2600-\u27BF\u200d\u2640-\u2642]',
                m['text'], re.UNICODE
            )
            s['emoji_count'] += len(emojis)
            lower = m['text'].lower()
            for token in BRAINROT_TOKENS:
                if token in lower:
                    s['brainrot_score'] += 1
        for sender, s in stats.items():
            s['avg_words'] = s['total_words'] / max(1, s['message_count'])
        return stats

    def _compute_response_times(self):
        intervals = defaultdict(list)
        prev = None
        for m in self.messages:
            if prev and m['sender'] != prev['sender']:
                delta = (m['timestamp'] - prev['timestamp']).total_seconds()
                if delta > 0:
                    intervals[m['sender']].append(delta)
            prev = m
        return {p: sum(v)/len(v) if v else float('inf') for p, v in intervals.items()}

    def _conversation_carrier(self, user):
        total = sum(len(m['text'].split()) for m in self.messages)
        user_total = sum(len(m['text'].split()) for m in self.messages if m['sender'] == user)
        return round((user_total / total) * 100, 1) if total else 0

    def _reply_gap_analysis(self, user, response_stats):
        other = [p for p in self.participants if p != user]
        other = other[0] if len(other) == 1 else None
        if not other:
            return {"user_avg": "N/A", "other_avg": "N/A", "comment": ""}

        def fmt(sec):
            if sec == float('inf'): return "never lmao"
            if sec < 60: return f"{int(sec)} seconds"
            if sec < 3600: return f"{int(sec/60)} minutes"
            if sec < 86400: return f"{round(sec/3600, 1)} hours"
            return f"{round(sec/86400, 1)} business days"

        u = response_stats.get(user, float('inf'))
        o = response_stats.get(other, float('inf'))
        comment = ""
        if u < 60 and o > 3600:
            comment = "you reply like it's your job. they reply like it's jury duty."
        elif o == float('inf'):
            comment = "they have never replied first. not once. think about that."
        elif u > 3600 and o < 60:
            comment = "oh. oh no. you're the one waiting by the phone. this is painful."
        return {"user_avg": fmt(u), "other_avg": fmt(o), "comment": comment}

    def _count_double_texts(self, user):
        count = 0
        for i in range(1, len(self.messages)):
            if self.messages[i]['sender'] == user and self.messages[i-1]['sender'] == user:
                count += 1
        return count

    def _crashout_detector(self, user):
        user_msgs = [m for m in self.messages if m['sender'] == user]
        if not user_msgs:
            return {"crashout": False, "reason": "", "time": ""}

        groups = []
        curr = [user_msgs[0]]
        for i in range(1, len(user_msgs)):
            delta = (user_msgs[i]['timestamp'] - user_msgs[i-1]['timestamp']).total_seconds()
            if delta < 120:
                curr.append(user_msgs[i])
            else:
                if len(curr) >= 5:
                    groups.append(curr)
                curr = [user_msgs[i]]
        if len(curr) >= 5:
            groups.append(curr)

        for g in groups:
            t = g[0]['timestamp']
            if t.hour >= NIGHT_START or t.hour < NIGHT_END:
                time_str = t.strftime('%I:%M %p').lstrip('0')
                reason = random.choice(CRASHOUT_PHRASES).format(time=time_str)
                return {"crashout": True, "reason": reason, "time": time_str}

        for m in user_msgs:
            words = len(m['text'].split())
            t = m['timestamp']
            if words > 80 and (t.hour >= NIGHT_START or t.hour < NIGHT_END):
                time_str = t.strftime('%I:%M %p').lstrip('0')
                return {"crashout": True, "reason": f"wrote a whole novel at {time_str}. that's not a text, that's a manuscript.", "time": time_str}
        return {"crashout": False, "reason": "", "time": ""}

    def _locked_in_detector(self, user):
        night = [m for m in self.messages if m['timestamp'].hour >= NIGHT_START or m['timestamp'].hour < NIGHT_END]
        u_night = [m for m in night if m['sender'] == user]
        o_night = [m for m in night if m['sender'] != user]
        if len(u_night) >= 5 and len(o_night) >= 5:
            intervals = []
            prev = None
            for m in night:
                if prev and m['sender'] == user and prev['sender'] != user:
                    d = (m['timestamp'] - prev['timestamp']).total_seconds()
                    if 0 < d:
                        intervals.append(d)
                prev = m
            if intervals and (sum(intervals)/len(intervals)) < 120:
                return {"locked_in": True, "comment": "this conversation had employment-level commitment. benefits not included."}
        return {"locked_in": False, "comment": ""}

    def _sleep_schedule_damage(self):
        night = [m for m in self.messages if m['timestamp'].hour >= NIGHT_START or m['timestamp'].hour < NIGHT_END]
        if len(night) > 5:
            return "both of you sacrificed REM sleep for whatever this is. your circadian rhythm is filing a complaint."
        return ""

    def _brainrot_analysis(self):
        score = sum(1 for m in self.messages for t in BRAINROT_TOKENS if t in m['text'].lower())
        if score > 15:
            return "mutual brainrot compatibility detected. you two share one brain cell and it's buffering."
        if score > 8:
            return "moderate brainrot. the skull emoji is doing heavy lifting in this relationship."
        if score > 3:
            return "mild brainrot tendencies. a few 'bro's, a couple '💀'. manageable."
        return ""

    def _aura_loss(self, user, double_texts, response_stats):
        loss = 0
        reasons = []
        if double_texts > 0:
            loss -= double_texts * 3
            reasons.append(f"double texted {double_texts} times like you were refreshing for a reply")
        other = [p for p in self.participants if p != user]
        other = other[0] if len(other) == 1 else None
        if other and response_stats.get(user, 999) < 60 and response_stats.get(other, 999) > 3600:
            loss -= 25
            reasons.append("reply time difference is actually embarrassing to look at")
        if loss == 0:
            return 0, "aura somehow intact. barely."
        return max(loss, -100), "; ".join(reasons)

    def _delusion_score(self, user, stats):
        other = [p for p in self.participants if p != user]
        if not other:
            return 50
        other = other[0]
        u = stats.get(user, {"message_count": 0, "total_words": 0})
        o = stats.get(other, {"message_count": 0, "total_words": 0})
        total = u['message_count'] + o['message_count']
        if total == 0:
            return 50
        ratio = u['message_count'] / total
        if ratio > 0.75: return random.randint(88, 98)
        if ratio > 0.65: return random.randint(76, 87)
        if ratio > 0.55: return random.randint(61, 75)
        return random.randint(10, 45)

    def _dry_texter_meter(self, user, stats):
        other = [p for p in self.participants if p != user]
        other = other[0] if len(other) == 1 else None
        if not other:
            return "N/A"
        s = stats[other]
        avg = s['avg_words']
        emoji_ratio = s['emoji_count'] / max(1, s['message_count'])
        if avg < 3 and emoji_ratio < 0.5: return "CRITICAL — drier than a saltine cracker"
        if avg < 5: return "high — they text like it costs per letter"
        if avg < 8: return "moderate — could use some enthusiasm"
        return "hydrated — actual sentences were found"

    def _attachment_imbalance(self, user, stats):
        other = [p for p in self.participants if p != user]
        other = other[0] if len(other) == 1 else None
        if not other:
            return "not enough data"
        u_words = stats[user]['total_words']
        o_words = stats[other]['total_words']
        ratio = u_words / max(1, o_words)
        if ratio > 3:
            return "you wrote a dissertation. they sent 'k'. this is not balanced."
        if ratio > 2:
            return "one of you is in love. the other one is replying during ad breaks."
        if ratio < 0.33:
            return "they're carrying this entire conversation on their back. you're a passenger."
        return "surprisingly mutual effort. rare sighting."

    def _pick_savage_verdict(self, user, delusion, double_texts, crashout, dry, stats):
        pool = SAVAGE_VERDICTS.copy()
        if delusion > 85:
            pool += [
                "the math is not mathing and you're the only one who doesn't see it.",
                "delusion level: you think they're busy. they posted on their story 4 times.",
            ]
        if double_texts > 15:
            pool.append("you've sent more unanswered messages than a customer support bot.")
        if crashout.get("crashout"):
            pool.append("that crashout belongs in a museum. absolute performance art.")
        if dry and dry.startswith("CRITICAL"):
            pool.append("talking to a brick wall would give you more emotional feedback.")
        return random.choice(pool)

    def _group_insights(self):
        stats = self._compute_participant_stats()
        resp = self._compute_response_times()
        participants = list(stats.keys())
        if not participants:
            return {}

        most = max(participants, key=lambda p: stats[p]['message_count'])
        yapper = max(participants, key=lambda p: stats[p]['total_words'])
        ghoster = max(participants, key=lambda p: resp.get(p, 0))
        dry = min(participants, key=lambda p: stats[p]['avg_words'])
        meme = max(participants, key=lambda p: stats[p]['brainrot_score'])
        npc = min(participants, key=lambda p: stats[p]['message_count'])
        crash = None
        for p in participants:
            if self._crashout_detector(p)['crashout']:
                crash = p
                break

        return {
            "most_annoying": f"{most} — wouldn't stop texting if the building was on fire",
            "biggest_yapper": f"{yapper} — sent enough words to fill a paperback",
            "ghoster": f"{ghoster} — replies slower than government paperwork",
            "dry_texter": f"{dry} — their texts have the emotional depth of a receipt",
            "meme_dealer": f"{meme} — single-handedly keeping the brainrot economy alive",
            "certified_npc": f"{npc} — barely participated. background character energy.",
            "hidden_crashout": f"{crash} — seems fine but the chat logs say otherwise" if crash else "none — somehow everyone kept it together"
        }