SELECT transaction_id, sender_id, sender_name, receiver_id, receiver_name, amount, timestamp
FROM paysim_demo.payments
WHERE receiver_type='merchant' AND high_risk AND amount>1000
ORDER BY amount DESC;
