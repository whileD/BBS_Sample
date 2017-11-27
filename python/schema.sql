CREATE TABLE threads (
  id INTEGER PRIMARY KEY,
  name TEXT
);

CREATE TABLE thread_responses (
  thread_id INTEGER,
  response_number INTEGER,
  response TEXT,
  user_name TEXT
);
