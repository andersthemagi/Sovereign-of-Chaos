USE discord;
SET foreign_key_checks = 0;

CREATE TABLE IF NOT EXISTS users (
  internal_user_id INT NOT NULL AUTO_INCREMENT,
  user_id CHAR(18) NOT NULL,
  xp INT,
  lvl INT,
  class_name VARCHAR(50),
  rank_name VARCHAR(50),
  daily_xp_earned BOOL,
  daily_xp_streak INT,
  last_message FLOAT(20, 8),
  messaged_today BOOL,
  PRIMARY KEY (internal_user_id)
);

CREATE TABLE IF NOT EXISTS server_registry (
  server_id CHAR(18) NOT NULL,
  user_id INT NOT NULL,
  PRIMARY KEY (server_id, user_id)
);

CREATE TABLE IF NOT EXISTS events (
  event_id INT NOT NULL AUTO_INCREMENT,
  user_id CHAR(18),
  category VARCHAR(10),
  eventTime VARCHAR(20),
  PRIMARY KEY (event_id)
);
