from datetime import datetime, timedelta
from database.users_chats_db import data_db

class VStatsDatabase:
    def __init__(self):
        # Using a dedicated collection for verification statistics
        self.vcol = data_db.VerificationStats 

    async def record_verification(self, user_id: int):
        """ᴜsᴇʀ ᴋɪ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴅᴇᴛᴀɪʟ ᴛɪᴍᴇsᴛᴀᴍᴘ ᴋᴇ sᴀᴀᴛʜ sᴀᴠᴇ ᴋᴀʀᴇɪɴ."""
        await self.vcol.insert_one({
            "user_id": user_id,
            "verified_at": datetime.now()
        })

    async def get_advanced_vstats(self):
        """ᴍᴏɴɢᴏᴅʙ ᴀɢɢʀᴇɢᴀᴛɪᴏɴ ᴘɪᴘᴇʟɪɴᴇ: ᴇᴋ ʙᴀᴀʀ ᴍᴇɪɴ sᴀᴀʀᴀ ᴅᴀᴛᴀ ꜰᴇᴛᴄʜ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ."""
        now = datetime.now()
        
        # Time boundary calculations
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        seven_days_ago = today_start - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_year_start = year_start.replace(year=year_start.year - 1)

        # Advanced single-trip aggregation pipeline
        pipeline = [
            {
                "$facet": {
                    "today": [{"$match": {"verified_at": {"$gte": today_start}}}, {"$count": "count"}],
                    "yesterday": [{"$match": {"verified_at": {"$gte": yesterday_start, "$lt": today_start}}}, {"$count": "count"}],
                    "seven_days": [{"$match": {"verified_at": {"$gte": seven_days_ago}}}, {"$count": "count"}],
                    "this_month": [{"$match": {"verified_at": {"$gte": month_start}}}, {"$count": "count"}],
                    "this_year": [{"$match": {"verified_at": {"$gte": year_start}}}, {"$count": "count"}],
                    "prev_year": [{"$match": {"verified_at": {"$gte": prev_year_start, "$lt": year_start}}}, {"$count": "count"}]
                }
            }
        ]
        
        cursor = self.vcol.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        data = result[0] if result else {}

        # Helper function to safely extract counts
        def extract_count(key):
            return data.get(key, [{}])[0].get("count", 0) if data.get(key) else 0

        # Returning clean dictionary for UI/Bot messages
        return {
            "today": extract_count("today"),
            "yesterday": extract_count("yesterday"),
            "seven_days": extract_count("seven_days"),
            "month": extract_count("this_month"),
            "year": extract_count("this_year"),
            "prev_year": extract_count("prev_year")
        }

vdb = VStatsDatabase()