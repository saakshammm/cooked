# nim_analyzer.py
# Max Amini style roaster via NVIDIA NIM — accuracy-forced prompt

import json
import re
from openai import OpenAI

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL_NAME = "meta/llama-3.1-8b-instruct"

class NIMChatAnalyzer:
    def __init__(self, raw_text, chat_type, user_name, api_key):
        self.raw = raw_text
        self.chat_type = chat_type
        self.user_name = user_name
        self.client = OpenAI(
            base_url=NIM_BASE_URL,
            api_key=api_key
        )

    async def run_analysis(self):
        truncated = self.raw[-8000:] if len(self.raw) > 8000 else self.raw

        system_prompt = """You are a comedian who roasts people by reading their chat and pointing out the funniest, most embarrassing real patterns. You speak like a brutally honest friend — Gen Z slang, internet brainrot, zero filter. You do NOT invent facts. You only roast things you actually see in the messages.

CRITICAL RULES:
- NEVER make up names. Only use names you can literally see in the chat messages.
- NEVER invent events, traumas, exes, or backstories unless they are explicitly stated in the chat.
- ALWAYS base every roast on actual message patterns: who texts more, who replies faster, who sends paragraphs vs one-word replies, who uses too many emojis, who double texts, who crashes out at 2am.
- If you can't determine who is who, pick the person who sends more messages as the "main character" being roasted.
- Your roasts should reference REAL QUOTES or REAL PATTERNS from the chat. If someone says "bro" 40 times, roast that. If someone sends 😭 after every message, roast that. If someone wrote a paragraph and got "k" back, roast that.
- Do NOT analyze trauma, relationships, or psychological conditions. This is about texting behavior only.
- The humor comes from HOW people text, not from diagnosing their life problems.

You MUST output a valid JSON object with these exact keys:

- delusion_score: integer 0-100. High score means one person is way more invested than the other. Base this on message count ratio, word count ratio, and who double texts more.
- double_texts: integer. Count how many times the more active person sent back-to-back messages without getting a reply.
- aura_loss: negative integer between 0 and -100. How much aura the main character lost through their texting behavior. 0 means perfect aura, -100 means completely cooked.
- aura_reason: one specific sentence about what they did to lose aura. Reference actual texting behavior you observed.
- dry_texter_meter: pick one: "CRITICAL — drier than a saltine cracker", "high — texts like it costs per letter", "moderate — could use some enthusiasm", "hydrated — actual sentences were found", "N/A"
- attachment_imbalance: one sentence about who clearly cares more, based on effort. Be specific about what you observed.
- sleep_damage: if there are messages between 11pm-5am, roast them for it. Empty string if the chat was during normal hours.
- brainrot: roast their overuse of internet slang, emojis, or meme language if you see it. Empty string if they text normally.
- crashout: object {"crashout": bool, "reason": string describing exactly what happened, "time": string like "2:14 AM"}. Only set true if you see actual rapid-fire messages, long paragraphs at night, or clear spiraling.
- locked_in: object {"locked_in": bool, "comment": string}. True if you see fast back-and-forth at night with long messages from both sides.
- carrier_percent: integer. What percentage of total words came from the more active person.
- reply_gap_user_avg: string describing the more active person's average reply time. Actually estimate it from the timestamps.
- reply_gap_other_avg: string describing the other person's average reply time.
- reply_gap_comment: one savage line about the reply time difference. Make it funny and true.
- verdict: THE FINAL ROAST. One devastating sentence that sums up why this chat is cooked. Must reference something real you saw. Put it in quotes. Max Amini energy — observational, specific, and destroys them while making them laugh.
- group_insights: null if direct chat. If group chat: object with most_annoying, biggest_yapper, ghoster, dry_texter, meme_dealer, certified_npc, hidden_crashout. Each value should be a funny label with the person's name and why.

COUNT ACCURATELY. If you see 4 double texts, say 4. Don't guess. The funny comes from truth, not fiction."""

        user_prompt = f"Chat type: {self.chat_type}\n\nHere is the chat. Read it carefully. Count things. Only roast what you actually see:\n\n{truncated}"

        try:
            completion = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1400,
                top_p=0.9
            )
            content = completion.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # ensure all keys exist with safe defaults
                result.setdefault("delusion_score", 50)
                result.setdefault("double_texts", 0)
                result.setdefault("aura_loss", 0)
                result.setdefault("aura_reason", "somehow kept their aura intact")
                result.setdefault("dry_texter_meter", "N/A")
                result.setdefault("attachment_imbalance", "could not determine from this chat")
                result.setdefault("sleep_damage", "")
                result.setdefault("brainrot", "")
                result.setdefault("crashout", {"crashout": False, "reason": "", "time": ""})
                result.setdefault("locked_in", {"locked_in": False, "comment": ""})
                result.setdefault("carrier_percent", 50)
                result.setdefault("reply_gap_user_avg", "N/A")
                result.setdefault("reply_gap_other_avg", "N/A")
                result.setdefault("reply_gap_comment", "")
                result.setdefault("verdict", "this chat is too normal to roast properly and somehow that's worse")
                result.setdefault("group_insights", None)
                # reshape reply_gap for frontend
                result["reply_gap"] = {
                    "user_avg": result.pop("reply_gap_user_avg", "N/A"),
                    "other_avg": result.pop("reply_gap_other_avg", "N/A"),
                    "comment": result.pop("reply_gap_comment", "")
                }
                result["user"] = self.user_name
                result["participants"] = []
                result["stats"] = {}
                return result
            else:
                return {"error": "AI couldn't parse the chat. Try again with a different export."}
        except Exception as e:
            return {"error": f"NIM API error: {str(e)}"}