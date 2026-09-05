SELECT * FROM GRAPH_TABLE (
  fraud_graph MATCH (c IS client)-[e IS used_device]->(d IS device)
  COLUMNS (*)
) LIMIT 100;
