SELECT DISTINCT a.identifier_id, a.kind, a.identifier,
       p.sender_id, p.sender_name, p.receiver_id, p.receiver_name,
       p.transaction_id, p.amount, p.timestamp
FROM paysim_demo.identifiers a
JOIN paysim_demo.identifiers b ON a.identifier_id=b.identifier_id AND a.client_id<>b.client_id
JOIN paysim_demo.payments p ON p.sender_id=a.client_id AND p.receiver_id=b.client_id
ORDER BY a.identifier_id, p.transaction_id;
