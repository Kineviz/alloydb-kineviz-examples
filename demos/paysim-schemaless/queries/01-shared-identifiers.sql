SELECT kind, identifier_id, identifier, count(DISTINCT client_id) AS accounts
FROM paysim_demo.identifiers GROUP BY kind, identifier_id, identifier
HAVING count(DISTINCT client_id)>1 ORDER BY accounts DESC, identifier;
