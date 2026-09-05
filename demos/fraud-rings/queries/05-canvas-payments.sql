SELECT p.src_client_id AS sender_id,s.name AS sender_name,p.tx_id AS transaction_id,
       p.amount,p.ts AS timestamp,p.dst_client_id AS receiver_id,r.name AS receiver_name
FROM fraud_demo.paid p JOIN fraud_demo.client s ON s.id=p.src_client_id
JOIN fraud_demo.client r ON r.id=p.dst_client_id ORDER BY p.tx_id LIMIT 500;
