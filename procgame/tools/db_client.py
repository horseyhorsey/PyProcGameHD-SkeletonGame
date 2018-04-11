import sqlite3
import logging
import os.path
import time


class GameDbClient(object):
    _current_folder = None
    """ Path to the game folder """

    _games_played_db = None
    """ Game history database """

    def __init__(self, game_folder, games_played_db):
        """ Creates a new database if the .db file doesn't exist """
        self.logger = logging.getLogger('db_client')

        self._current_folder = game_folder
        self._games_played_db = games_played_db

        if not self._database_exists():
            self._generate_new_database()

        self._update_db_views()

    def _generate_new_database(self):
        """ Creates an empty GameHistory.db tables and views """
        conn = self._connection()
        with conn:
            cur = conn.cursor()
            cur.executescript(self._create_db_string)
            cur.close()

    def _update_db_views(self):
        conn = self._connection()
        with conn:
            cur = conn.cursor()
            cur.executescript(self._latest_scores_view)
            cur.close()

    def _database_exists(self):
        game_played_db = self._get_db_path()
        return os.path.exists(game_played_db)

    def _get_db_path(self):
        return os.path.join(self._current_folder, self._games_played_db)

    def add_player(self, name):
        """ Adds a player to database and returns their ID """
        conn = self._connection()
        with conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO PLAYERS (Name) VALUES(?)", (name,))
            return cur.lastrowid

    def get_player_id(self, name):
        """ Returns player id for exact match of player name"""
        conn = self._connection()
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT PlayerId FROM PLAYERS WHERE NAME = ?", (name,))
            return cur.fetchone()

    def _connection(self):
        """ Gets the GameHistory Db Connection """
        game_played_db = self._get_db_path()
        return sqlite3.connect(game_played_db)

    def save_game_played(self, start_time, end_time, players, balls_per_game=None, ball_save_time=None):

        """ Players names containing "Player" (which is default pyprocgame) will be added into database as the default ID 1
        """

        plys = [[None, None, None], [None, None, None], [None, None, None], [None, None, None]]
        """ Each players (ID, Score) """

        if self._database_exists():
            conn = self._connection()
            with conn:
                cur = conn.cursor()

                _id = 1
                p_count = 1

                for p in players:
                    if "Player" not in p.name:
                        row = self.get_player_id(p.name)
                        if row is None:
                            _id = self.add_player(p.name)
                        else:
                            _id = row[0]

                    plys[p_count - 1] = [_id, p.score, int(p.game_time)]

                    p_count += 1
                cur.execute(
                    "INSERT INTO GamesPlayed (P1Id, P1Score, P1BallTime, P2Id, P2Score, P2BallTime, P3Id, P3Score, P3BallTime, P4Id, P4Score, P4BallTime, Started, Ended, BallsPerGame, BallSaveTime) Values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (plys[0][0], plys[0][1], plys[0][2], plys[1][0], plys[1][1], plys[1][2], plys[2][0], plys[2][1], plys[2][2], plys[3][0], plys[3][1], plys[3][2],
                     start_time, end_time, balls_per_game, ball_save_time))

                cur.close()

    _create_db_string = """
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS GamesPlayed;

-- Table: GamesPlayed
CREATE TABLE GamesPlayed (GamesPlayedId INTEGER PRIMARY KEY, P1Id INTEGER NOT NULL, P1Score INTEGER NOT NULL, P2Id INTEGER, P2Score INTEGER, P3Id INTEGER, P3Score INTEGER, P4Id INTEGER, P4Score INTEGER, BallsPerGame INTEGER (1, 10), BallSaveTime INTEGER (0, 120), P1ExtraBalls INTEGER (0, 20), P2ExtraBalls INTEGER (0, 20), P3ExtraBalls INTEGER (0, 20), P4ExtraBalls INTEGER (0, 20), Started DATETIME, Ended DATETIME, P1BallTime INTEGER, P2BallTime INTEGER, P3BallTime INTEGER, P4BallTime INTEGER, FOREIGN KEY (P1Id) REFERENCES Players (PlayerId), FOREIGN KEY (P2Id) REFERENCES Players (PlayerId), FOREIGN KEY (P3Id) REFERENCES Players (PlayerId), FOREIGN KEY (P4Id) REFERENCES Players (PlayerId));

-- Table: Players
CREATE TABLE Players(PlayerId INTEGER PRIMARY KEY, Name TEXT);
INSERT INTO Players (PlayerId, Name) VALUES (1, 'DEFAULT');

    """

    _latest_scores_view = """
    CREATE VIEW IF NOT EXISTS LatestScores AS
    SELECT *
      FROM GamesPlayed
           LEFT JOIN
           Players AS P1 ON GamesPlayed.P1Id = P1.PlayerId
           LEFT JOIN
           Players AS P2 ON GamesPlayed.P2Id = P2.PlayerId
           LEFT JOIN
           Players AS P3 ON GamesPlayed.P3Id = P3.PlayerId
           LEFT JOIN
           Players AS P4 ON GamesPlayed.P4Id = P4.PlayerId
     ORDER BY Started ASC;

    """