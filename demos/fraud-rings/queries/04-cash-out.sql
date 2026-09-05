SELECT p.tx_id,p.client_id,c.name AS client_name,p.merchant_id,m.name AS merchant_name,p.amount,p.ts
FROM fraud_demo.paidmerchant p JOIN fraud_demo.client c ON c.id=p.client_id
JOIN fraud_demo.merchant m ON m.id=p.merchant_id ORDER BY p.amount DESC;
