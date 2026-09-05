SELECT client_id, client_name, identifier_id, identifier, kind
FROM paysim_demo.identifiers
WHERE identifier_id IN (
  SELECT identifier_id FROM paysim_demo.identifiers
  GROUP BY identifier_id HAVING count(DISTINCT client_id)>1
) ORDER BY identifier_id, client_id;
