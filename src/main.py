import argparse
import sqlite3
from datetime import datetime
from fuzzywuzzy import fuzz


class Friend:
    def __init__(self, name, last_spoken=None):
        self.name = name
        self.last_spoken = self._parse_last_spoken(last_spoken)
    
    def _parse_last_spoken(self, last_spoken):
        if isinstance(last_spoken, str):
            try:
                return datetime.strptime(last_spoken, "%Y-%m-%d %I:%M:%S %p")
            except ValueError:
                try:
                    return datetime.strptime(last_spoken, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    return datetime.strptime(last_spoken, "%Y-%m-%d %H:%M:%S")
        return last_spoken

    def update_last_spoken(self, time=None):
        if time is None:
            time = input("Enter the time (or 'now' for current time): ")
        
        if time.lower() == "now":
            self.last_spoken = datetime.now()
        else:
            try:
                self.last_spoken = datetime.strptime(time, "%Y-%m-%d %I:%M:%S %p")
            except ValueError:
                print("Invalid time format. Please use 'YYYY-MM-DD HH:MM:SS AM/PM'.")
    
    def get_days_since_spoken(self):
        if self.last_spoken:
            time_diff = datetime.now() - self.last_spoken
            return time_diff.days
        else:
            return None


class FriendTracker:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.db_file)
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS friends (name TEXT PRIMARY KEY, last_spoken TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS friend_records (name TEXT, last_spoken TEXT, topic TEXT)")
        self.connection.commit()
    
    def close(self):
        if self.connection:
            self.connection.close()
    
    def add_friend(self, name):
        last_spoken = input("Enter the last spoken date and time (YYYY-MM-DD HH:MM:SS AM/PM or 'now' for current time): ")
        topic = input("Enter the topic of discussion: ")
        
        if last_spoken.lower() == "now":
            last_spoken = datetime.now()
        else:
            try:
                last_spoken = datetime.strptime(last_spoken, "%Y-%m-%d %I:%M:%S %p")
            except ValueError:
                print("Invalid date and time format. Please use 'YYYY-MM-DD HH:MM:SS AM/PM'.")
                return
        
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO friends (name, last_spoken) VALUES (?, ?)", (name, last_spoken.strftime("%Y-%m-%d %H:%M:%S")))
        self.connection.commit()
        
        if topic:
            self._record_last_spoken_topic(name, last_spoken, topic)

    
    def read_friends(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, last_spoken FROM friends")
        rows = cursor.fetchall()
        
        for row in rows:
            name, last_spoken = row
            friend = Friend(name, last_spoken)
            print(f"Friend: {friend.name}")
            if friend.last_spoken:
                days_since_spoken = friend.get_days_since_spoken()
                last_spoken_formatted = friend.last_spoken.strftime("%Y-%m-%d %I:%M:%S %p")
                print(f"Last Spoken: {last_spoken_formatted}")
                print(f"Days Since Last Spoken: {days_since_spoken}")
                self._display_friend_records(name)
            else:
                print("Last Spoken: Not available")
            print("-------------------")
    
    def _display_friend_records(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT last_spoken, topic FROM friend_records WHERE name=?", (name,))
        rows = cursor.fetchall()

        for row in rows:
            last_spoken, topic = row
            last_spoken_formatted = datetime.strptime(last_spoken, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %I:%M:%S %p")
            print(f"Last Spoken: {last_spoken_formatted}")
            print(f"Topic: {topic}")
            print("-------------------")

    def update_last_spoken(self, name, time=None):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM friends WHERE name=?", (name,))
        row = cursor.fetchone()

        if row:
            friend = Friend(row[0])
            friend.update_last_spoken(time)
            cursor.execute("UPDATE friends SET last_spoken=? WHERE name=?", (friend.last_spoken.strftime("%Y-%m-%d %H:%M:%S.%f"), friend.name))
            self.connection.commit()
            print(f"Updated last spoken time for {friend.name}")
            topic = input("Enter the topic of discussion: ")
            self._record_last_spoken_topic(friend.name, friend.last_spoken, topic)
        else:
            print(f"Friend '{name}' not found.")

    def _record_last_spoken_topic(self, name, last_spoken, topic=None):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO friend_records (name, last_spoken, topic) VALUES (?, ?, ?)", (name, last_spoken, topic))
        self.connection.commit()

    
    def delete_friend(self, name):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM friends WHERE name=?", (name,))
        cursor.execute("DELETE FROM friend_records WHERE name=?", (name,))
        self.connection.commit()
        
        if cursor.rowcount > 0:
            print(f"Deleted friend: {name}")
        else:
            print(f"Friend '{name}' not found.")
    
    def search_by_days_since_spoken(self, days):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, last_spoken FROM friends")
        rows = cursor.fetchall()
        
        for row in rows:
            name, last_spoken = row
            friend = Friend(name, last_spoken)
            days_since_spoken = friend.get_days_since_spoken()
            
            if days_since_spoken and days_since_spoken >= days:
                last_spoken_formatted = friend.last_spoken.strftime("%Y-%m-%d %I:%M:%S %p")
                print(f"Friend: {friend.name}")
                print(f"Last Spoken: {last_spoken_formatted}")
                print(f"Days Since Last Spoken: {days_since_spoken}")
                self._display_friend_records(name)
                print("-------------------")
    
    def search_by_topic(self, topic):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, topic FROM friend_records")
        rows = cursor.fetchall()

        results = []
        for row in rows:
            name = row[0]
            record_topic = row[1]
            similarity = fuzz.token_set_ratio(topic, record_topic)
            results.append((name, similarity, record_topic))

        results.sort(key=lambda x: x[1], reverse=True)

        if len(results) == 0:
            print(f"No results for {topic}")
        else:
            for result in results:
                name = result[0]
                similarity = result[1]
                record_topic = result[2]
                cursor.execute("SELECT last_spoken FROM friends WHERE name=?", (name,))
                last_spoken = cursor.fetchone()[0]
                friend = Friend(name, last_spoken)
                last_spoken_formatted = friend.last_spoken.strftime("%Y-%m-%d %I:%M:%S %p")
                print(f"Friend: {friend.name}")
                print(f"Last Spoken: {last_spoken_formatted}")
                print(f"Topic: {record_topic}")
                print("-------------------")

    def check_friend(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, last_spoken FROM friends WHERE name=?", (name,))
        row = cursor.fetchone()
        
        if row:
            name, last_spoken = row
            friend = Friend(name, last_spoken)
            print(f"Friend: {friend.name}")
            if friend.last_spoken:
                last_spoken_formatted = friend.last_spoken.strftime("%Y-%m-%d %I:%M:%S %p")
                print(f"Last Spoken: {last_spoken_formatted}")
                days_since_spoken = friend.get_days_since_spoken()
                print(f"Days Since Last Spoken: {days_since_spoken}")
                self._display_friend_records(name)
            else:
                print("Last Spoken: Not available")
        else:
            print(f"Friend '{name}' not found.")

    def display_help(self):
        print("Usage: python script.py [OPTIONS]")
        print()
        print("Options:")
        print("  --add NAME                  Add a friend")
        print("  --read                      Read list of all friends and last time spoken to")
        print("  --update NAME               Update the last time spoken to a friend")
        print("  --delete NAME               Delete a friend from the list")
        print("  --check NAME                Check the last time spoken to a friend and days since then")
        print("  --days-since DAYS           Search for friends based on days since last spoken")
        print("  --topic TOPIC               Search for friends based on topic of discussion")
        print("  --dbfile DBFILE             SQLite database file (default: friendex.db)")
        print("  --help                      Show this help message")

def main():
    parser = argparse.ArgumentParser(description="Friend Tracker CLI")
    parser.add_argument("--add", metavar="NAME", help="Add a friend")
    parser.add_argument("--read", action="store_true", help="Read list of all friends and last time spoken to")
    parser.add_argument("--update", metavar="NAME", help="Update the last time spoken to a friend")
    parser.add_argument("--delete", metavar="NAME", help="Delete a friend from the list")
    parser.add_argument("--check", metavar="NAME", help="Check the last time spoken to a friend and days since then")
    parser.add_argument("--days-since", metavar="DAYS", type=int, help="Search for friends based on days since last spoken")
    parser.add_argument("--topic", metavar="TOPIC", help="Search for friends based on topic of discussion")
    parser.add_argument("--dbfile", metavar="DBFILE", default="friendex.db", help="SQLite database file")

    args = parser.parse_args()

    friend_tracker = FriendTracker(args.dbfile)
    friend_tracker.connect()

    if args.add:
        friend_tracker.add_friend(args.add)
        print(f"Added friend: {args.add}")

    if args.read:
        friend_tracker.read_friends()

    if args.update:
        friend_tracker.update_last_spoken(args.update)

    if args.delete:
        friend_tracker.delete_friend(args.delete)

    if args.check:
        friend_tracker.check_friend(args.check)
    
    if args.days_since:
        friend_tracker.search_by_days_since_spoken(args.days_since)
    
    if args.topic:
        friend_tracker.search_by_topic(args.topic)

    friend_tracker.close()

if __name__ == "__main__":
    main()
