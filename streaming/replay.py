#!/usr/bin/env python3
"""Replay generated PaySim events, directly or through local Kafka; never reset data."""
import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from demo import ROOT, connect, owned, preflight, verify
from psycopg.types.json import Jsonb


def graph_rows(row):
    step = int(row['global_step'])
    if step < 1 or not math.isfinite(float(row['amount'])) or float(row['amount']) < 0:
        raise ValueError('Invalid transaction step/amount')
    if row['receiver_type'] not in {'CLIENT','MULE','MERCHANT','BANK'}:
        raise ValueError('Unsupported receiver type')
    if row['action'] not in {'CASH_IN','CASH_OUT','DEBIT','PAYMENT','TRANSFER'}:
        raise ValueError('Unsupported payment action')
    datetime.fromisoformat(row['ts'])
    if row['is_fraud'] not in {'true','false'} or row['is_flagged_fraud'] not in {'true','false'}:
        raise ValueError('Invalid boolean')
    tx = f'transaction_T{step:06d}'
    receiver = {'MERCHANT':'merchant','BANK':'bank'}.get(row['receiver_type'], 'client')
    props = dict(amount=round(float(row['amount']),2), timestamp=row['ts'], action=row['action'],
                 globalstep=step, isfraud=row['is_fraud']=='true',
                 isflaggedfraud=row['is_flagged_fraud']=='true',
                 typeorig=row['sender_type'], typedest=row['receiver_type'])
    node = (tx, 'transaction', props)
    edges = [('client_'+row['sender_id'],tx,f'p{step}','performs',{'timestamp':row['ts']}),
             (tx,receiver+'_'+row['receiver_id'],f't{step}','to_'+receiver,{'timestamp':row['ts']})]
    return node,edges


def land(conn, rows):
    # Nodes and both edges commit atomically. Foreign keys require seeded actors.
    with conn.transaction():
        owned(conn, 'paysim_demo')
        with conn.cursor() as cur:
            nodes,edges = [],[]
            for row in rows:
                n,ee = graph_rows(row)
                nodes.append((*n[:2],Jsonb(n[2])))
                edges.extend((*e[:4],Jsonb(e[4])) for e in ee)
            cur.executemany('INSERT INTO graphnode VALUES (%s,%s,%s) ON CONFLICT DO NOTHING',nodes)
            cur.executemany('INSERT INTO graphedge VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',edges)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--via',choices=['direct','kafka'],default='direct')
    p.add_argument('--seconds',type=float,default=60,help='target duration; 0 runs unpaced')
    p.add_argument('--bootstrap',default='127.0.0.1:19096')
    args = p.parse_args()
    if not math.isfinite(args.seconds) or args.seconds<0:
        p.error('--seconds must be finite and nonnegative')
    with (ROOT/'generated/paysim-schemaless/transactions.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        graph_rows(row)  # validate before committing any data
    producer=consumer=admin=None
    try:
        with connect() as conn:
            preflight(conn)
            owned(conn,'paysim_demo')
            conn.commit()
            if args.via=='kafka':
                from kafka import KafkaAdminClient,KafkaConsumer,KafkaProducer
                from kafka.admin import NewTopic
                topic='alloydb.paysim.'+uuid.uuid4().hex
                admin=KafkaAdminClient(bootstrap_servers=args.bootstrap)
                admin.create_topics([NewTopic(topic,num_partitions=1,replication_factor=1)])
                producer=KafkaProducer(bootstrap_servers=args.bootstrap,acks='all')
                consumer=KafkaConsumer(topic,bootstrap_servers=args.bootstrap,
                    group_id=topic+'.sink',auto_offset_reset='earliest',enable_auto_commit=False,
                    max_poll_records=100)
                print('Kafka topic:',topic,flush=True)
            start=time.monotonic()
            landed=0
            for i in range(0,len(rows),100):
                due=start+args.seconds*i/max(len(rows)-1,1)
                time.sleep(max(0,due-time.monotonic()))
                batch=rows[i:i+100]
                if producer:
                    futures=[producer.send(topic,value=json.dumps(row).encode()) for row in batch]
                    for future in futures:
                        future.get(timeout=30)
                    received=[]
                    deadline=time.monotonic()+60
                    while len(received)<len(batch):
                        if time.monotonic()>deadline:
                            raise TimeoutError('Kafka sink timed out')
                        polled=consumer.poll(timeout_ms=1000,max_records=len(batch)-len(received))
                        received.extend(json.loads(m.value.decode()) for messages in polled.values() for m in messages)
                    batch=received
                land(conn,batch)
                if consumer:
                    consumer.commit()  # after PostgreSQL commit, never before
                landed+=len(batch)
                if landed%1000==0 or landed==len(rows):
                    print(f'{landed}/{len(rows)} landed',flush=True)
            verify(conn,'paysim-schemaless')
            print(f'Replay verified ({args.via}), elapsed {time.monotonic()-start:.1f}s. No data reset.')
    finally:
        for client in (consumer,producer,admin):
            if client:
                client.close()


if __name__=='__main__':
    main()
