CREATE TABLE IF NOT EXISTS graphnode (
  id text PRIMARY KEY, label text NOT NULL,
  properties jsonb NOT NULL CHECK (jsonb_typeof(properties) = 'object')
);
CREATE TABLE IF NOT EXISTS graphedge (
  id text REFERENCES graphnode(id), dest_id text REFERENCES graphnode(id),
  edge_id text NOT NULL, label text NOT NULL, properties jsonb NOT NULL,
  PRIMARY KEY (id, dest_id, edge_id)
);
CREATE INDEX IF NOT EXISTS node_label ON graphnode(label);
CREATE INDEX IF NOT EXISTS edge_destination ON graphedge(dest_id, label, id);
CREATE INDEX IF NOT EXISTS edge_label ON graphedge(label, id, dest_id);
CREATE OR REPLACE VIEW identifiers AS
SELECT c.id AS client_id, c.properties->>'name' AS client_name,
       i.id AS identifier_id, i.label AS kind, i.properties->>'name' AS identifier
FROM graphnode c JOIN graphedge e ON e.id=c.id
JOIN graphnode i ON i.id=e.dest_id
WHERE c.label='client' AND e.label IN ('has_ssn','has_email','has_phone');
CREATE OR REPLACE VIEW payments AS
SELECT t.id AS transaction_id, s.id AS sender_id, s.properties->>'name' AS sender_name,
       r.id AS receiver_id, r.label AS receiver_type, r.properties->>'name' AS receiver_name,
       (t.properties->>'amount')::numeric AS amount,
       (t.properties->>'timestamp')::timestamptz AS timestamp,
       t.properties->>'action' AS action,
       COALESCE((r.properties->>'highrisk')::boolean, false) AS high_risk
FROM graphnode t JOIN graphedge p ON p.dest_id=t.id AND p.label='performs'
JOIN graphnode s ON s.id=p.id
JOIN graphedge d ON d.id=t.id AND d.label IN ('to_client','to_merchant','to_bank')
JOIN graphnode r ON r.id=d.dest_id WHERE t.label='transaction';
