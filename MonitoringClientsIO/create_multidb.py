#!/usr/bin/env python
import sqlite3

with open('lustre-OST','r') as f:
	ost_list = f.readlines()
	
	for line in ost_list:
		line=line.strip()
		conn = sqlite3.connect('{}.db'.format(line))
		print 'Open {}.db successfully.'.format(line)
		cursor=conn.cursor()
		sql = 'create table {} (c_name char(30) not null,s_time real,r_bytes real,w_bytes real,r_rates real,w_rates real);'.format(line)
		cursor.execute(sql)
		cursor.execute('create index {}_index on {} (c_name) ; '.format(line,line))
		print 'Create table %s successfully.' %line
