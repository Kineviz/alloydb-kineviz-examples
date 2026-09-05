SELECT * FROM GRAPH_TABLE (
  paysim_graph MATCH (a IS client)-[p IS performs]->(t IS transaction)-[d IS to_client]->(b IS client)
  COLUMNS (*)
) LIMIT 100;
