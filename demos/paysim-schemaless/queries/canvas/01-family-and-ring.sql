-- Kineviz graph-mode shorthand: COLUMNS (*) is expanded by the connector.
-- Use queries/pgq for SQL executed directly by psql.
SELECT * FROM GRAPH_TABLE (
  paysim_graph MATCH (c IS client)-[e IS has_phone]->(p IS phonenumber)
  COLUMNS (*)
) LIMIT 100;
