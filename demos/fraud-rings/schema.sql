CREATE TABLE IF NOT EXISTS client (id text PRIMARY KEY, name text, email text, opened_date date, risk_tier text);
CREATE TABLE IF NOT EXISTS device (id text PRIMARY KEY, kind text, first_seen date);
CREATE TABLE IF NOT EXISTS merchant (id text PRIMARY KEY, name text, category text);
CREATE TABLE IF NOT EXISTS useddevice (
  client_id text REFERENCES client(id), device_id text REFERENCES device(id), first_used date,
  PRIMARY KEY(client_id,device_id)
);
CREATE TABLE IF NOT EXISTS paid (
  tx_id text PRIMARY KEY, src_client_id text NOT NULL REFERENCES client(id),
  dst_client_id text NOT NULL REFERENCES client(id), amount numeric(18,2), ts timestamptz
);
CREATE TABLE IF NOT EXISTS paidmerchant (
  tx_id text PRIMARY KEY, client_id text NOT NULL REFERENCES client(id),
  merchant_id text NOT NULL REFERENCES merchant(id), amount numeric(18,2), ts timestamptz
);
CREATE INDEX IF NOT EXISTS device_holders ON useddevice(device_id,client_id);
CREATE INDEX IF NOT EXISTS payment_pairs ON paid(src_client_id,dst_client_id);
