-- SQL/PGQ uses declared labels. Filtered views adapt the flexible JSONB store;
-- this is NOT Spanner DYNAMIC LABEL / DYNAMIC PROPERTIES support.
CREATE VIEW client_v AS SELECT id,properties->>'name' AS name FROM graphnode WHERE label='client';
CREATE VIEW merchant_v AS SELECT id,properties->>'name' AS name,(properties->>'highrisk')::boolean AS highrisk FROM graphnode WHERE label='merchant';
CREATE VIEW bank_v AS SELECT id,properties->>'name' AS name FROM graphnode WHERE label='bank';
CREATE VIEW email_v AS SELECT id,properties->>'name' AS name FROM graphnode WHERE label='email';
CREATE VIEW phone_v AS SELECT id,properties->>'name' AS name FROM graphnode WHERE label='phonenumber';
CREATE VIEW ssn_v AS SELECT id,properties->>'name' AS name FROM graphnode WHERE label='ssn';
CREATE VIEW transaction_v AS
SELECT id,(properties->>'amount')::numeric AS amount,(properties->>'timestamp')::timestamptz AS timestamp,
       properties->>'action' AS action FROM graphnode WHERE label='transaction';
-- A single stable edge key is exposed for the Desktop connector.
CREATE VIEW performs_v AS SELECT jsonb_build_array(id,dest_id,edge_id)::text AS eid,id,dest_id FROM graphedge WHERE label='performs';
CREATE VIEW to_client_v AS SELECT jsonb_build_array(id,dest_id,edge_id)::text AS eid,id,dest_id FROM graphedge WHERE label='to_client';
CREATE VIEW to_merchant_v AS SELECT jsonb_build_array(id,dest_id,edge_id)::text AS eid,id,dest_id FROM graphedge WHERE label='to_merchant';
CREATE VIEW to_bank_v AS SELECT jsonb_build_array(id,dest_id,edge_id)::text AS eid,id,dest_id FROM graphedge WHERE label='to_bank';
CREATE VIEW has_email_v AS SELECT jsonb_build_array(id,dest_id,edge_id)::text AS eid,id,dest_id FROM graphedge WHERE label='has_email';
CREATE VIEW has_phone_v AS SELECT jsonb_build_array(id,dest_id,edge_id)::text AS eid,id,dest_id FROM graphedge WHERE label='has_phone';
CREATE VIEW has_ssn_v AS SELECT jsonb_build_array(id,dest_id,edge_id)::text AS eid,id,dest_id FROM graphedge WHERE label='has_ssn';
CREATE PROPERTY GRAPH paysim_graph
VERTEX TABLES (
  client_v KEY(id) LABEL client PROPERTIES(id,name),
  merchant_v KEY(id) LABEL merchant PROPERTIES(id,name,highrisk),
  bank_v KEY(id) LABEL bank PROPERTIES(id,name),
  email_v KEY(id) LABEL email PROPERTIES(id,name),
  phone_v KEY(id) LABEL phonenumber PROPERTIES(id,name),
  ssn_v KEY(id) LABEL ssn PROPERTIES(id,name),
  transaction_v KEY(id) LABEL transaction PROPERTIES(id,amount,timestamp,action)
)
EDGE TABLES (
  performs_v KEY(eid) SOURCE KEY(id) REFERENCES client_v(id) DESTINATION KEY(dest_id) REFERENCES transaction_v(id) LABEL performs PROPERTIES(eid),
  to_client_v KEY(eid) SOURCE KEY(id) REFERENCES transaction_v(id) DESTINATION KEY(dest_id) REFERENCES client_v(id) LABEL to_client PROPERTIES(eid),
  to_merchant_v KEY(eid) SOURCE KEY(id) REFERENCES transaction_v(id) DESTINATION KEY(dest_id) REFERENCES merchant_v(id) LABEL to_merchant PROPERTIES(eid),
  to_bank_v KEY(eid) SOURCE KEY(id) REFERENCES transaction_v(id) DESTINATION KEY(dest_id) REFERENCES bank_v(id) LABEL to_bank PROPERTIES(eid),
  has_email_v KEY(eid) SOURCE KEY(id) REFERENCES client_v(id) DESTINATION KEY(dest_id) REFERENCES email_v(id) LABEL has_email PROPERTIES(eid),
  has_phone_v KEY(eid) SOURCE KEY(id) REFERENCES client_v(id) DESTINATION KEY(dest_id) REFERENCES phone_v(id) LABEL has_phone PROPERTIES(eid),
  has_ssn_v KEY(eid) SOURCE KEY(id) REFERENCES client_v(id) DESTINATION KEY(dest_id) REFERENCES ssn_v(id) LABEL has_ssn PROPERTIES(eid)
);
