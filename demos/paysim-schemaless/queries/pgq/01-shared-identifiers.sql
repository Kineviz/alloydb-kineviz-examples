SELECT identifier,count(DISTINCT client_id) AS accounts FROM GRAPH_TABLE (
  paysim_demo.paysim_graph
  MATCH (c IS client)-[e IS has_ssn|has_email|has_phone]->(i)
  COLUMNS (c.id AS client_id, i.id AS identifier)
) GROUP BY identifier HAVING count(DISTINCT client_id)>1 ORDER BY identifier;
