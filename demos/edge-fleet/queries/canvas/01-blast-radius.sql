SELECT * FROM GRAPH_TABLE (
  fleet_graph MATCH (d IS device)-[e IS connected_to]->(g IS gateway)-[h IS hosted_at]->(s IS site)
  COLUMNS (*)
) LIMIT 100;
