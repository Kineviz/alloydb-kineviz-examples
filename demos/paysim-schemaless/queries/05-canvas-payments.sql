-- Flat, scalar columns for Kineviz's SQL Mapping Editor. No JSON/GQL parsing.
SELECT sender_id, sender_name, transaction_id, amount, timestamp, action,
       receiver_id, receiver_name, receiver_type
FROM paysim_demo.payments
WHERE receiver_type='client'
ORDER BY timestamp, transaction_id LIMIT 500;
