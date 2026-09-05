SELECT * FROM GRAPH_TABLE (
  paysim_demo.paysim_graph
  MATCH (a IS client)-[p IS performs]->(t IS transaction)-[d IS to_client]->(b IS client)
  COLUMNS (a.id AS sender,t.id AS transaction_id,t.amount AS amount,b.id AS receiver)
) ORDER BY transaction_id LIMIT 100;
