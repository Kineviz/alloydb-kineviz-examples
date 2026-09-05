SELECT dst_client_id, count(DISTINCT src_client_id) AS senders, sum(amount) AS total
FROM fraud_demo.paid GROUP BY dst_client_id
HAVING count(DISTINCT src_client_id)>=3 ORDER BY total DESC;
