# friendex

![image](/friendex_logo.png)

Friendex is a command-line module for tracking and managing friendships. It allows you to keep track of friends, the last time you spoke to them, and the topics of discussion. The module uses SQLite as a database to store friend information.

## Installation

1. Clone the repository or download the module files.
2. Make sure you have Python 3 installed on your system.
3. Install the required dependencies by running the following command:
   
   ```
   pip install -r requirements.txt
   ```

## Usage

To use Friendex, navigate to the `src` directory in the terminal and run the `main.py` script with appropriate command-line arguments.

```
python main.py [OPTIONS]
```

### Options

- `--add NAME`: Add a friend to the list.
- `--read`: Read the list of all friends and their last spoken time.
- `--update NAME`: Update the last time spoken to a friend.
- `--delete NAME`: Delete a friend from the list.
- `--check NAME`: Check the last time spoken to a friend and the number of days since then.
- `--days-since DAYS`: Search for friends based on the number of days since the last spoken time.
- `--topic TOPIC`: Search for friends based on the topic of discussion.
- `--dbfile DBFILE`: SQLite database file (default: friendex.db).
- `--help`: Show the help message.

Note: Replace `NAME` with the name of the friend and `DAYS` with the desired number of days.

### Examples

Add a friend:
```
python main.py --add John
```

Read the list of all friends:
```
python main.py --read
```

Update the last time spoken to a friend:
```
python main.py --update John
```

Delete a friend from the list:
```
python main.py --delete John
```

Check the last time spoken to a friend and the number of days since then:
```
python main.py --check John
```

Search for friends based on the number of days since the last spoken time:
```
python main.py --days-since 30
```

Search for friends based on the topic of discussion:
```
python main.py --topic "sports"
```

## Database

Friendex uses an SQLite database to store friend information. By default, the database file is `friendex.db`. You can specify a different database file using the `--dbfile` option.

## License

This module is released under the MIT License. See the [license](license.txt) file for more details.
