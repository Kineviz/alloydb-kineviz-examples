SELECT receiver_id, receiver_name, count(DISTINCT sender_id) AS senders,
       count(*) AS transfers, sum(amount) AS total
FROM paysim_demo.payments WHERE receiver_type='client' AND action='TRANSFER'
GROUP BY receiver_id, receiver_name HAVING count(DISTINCT sender_id)>=3
ORDER BY total DESC;
