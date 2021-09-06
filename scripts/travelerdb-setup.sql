USE discord;
DROP TABLE IF EXISTS events;
CREATE TABLE IF NOT EXISTS events (
  event_id INT NOT NULL AUTO_INCREMENT,
  server_id CHAR(18),
  user_id CHAR(18),
  category VARCHAR(10),
  event_time CHAR(5),
  PRIMARY KEY (event_id)
);
INSERT INTO events
  (event_id, server_id, user_id, category, event_time)
VALUES 
  (NULL, "703015465076785263", "197158011469299713", "tarot", "08:00");
