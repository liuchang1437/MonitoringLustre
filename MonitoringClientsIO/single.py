#!/usr/bin/env python
import paramiko
import time
import sqlite3
import time
import sys

def client_io():
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect("io01",22,"hpclc", "lc940108")
	#print 'Connect to io01 successfully.'
	cur_OST=sys.argv[1]
	cur_table=cur_OST.replace('-','_')
	conn = sqlite3.connect('{}.db'.format(cur_table))
	cursor=conn.cursor()
	#print 'Open {}.db successfully.'.format(cur_table)

	cwd = '/proc/fs/lustre/obdfilter/'
	flag=True
	
	num_exports=int(ssh.exec_command('cat %s%s/num_exports' %(cwd ,cur_OST))[1].readline().strip('\n'))
	clients_list=ssh.exec_command('ls %s%s/exports/' %(cwd,cur_OST))[1]
	for j in range(0,num_exports):
		cur_client=clients_list.readline().strip('\n')
		snapshot_time=0
		read_bytes=0
		write_bytes=0
		stats_list = ssh.exec_command('cat %s%s/exports/%s/stats' %(cwd ,cur_OST ,cur_client) )[1].readlines()
		for line in stats_list:
			value_vlaue = line.split()
			if value_vlaue[0]=='snapshot_time':
				snapshot_time=float(value_vlaue[1])
			if value_vlaue[0]=='read_bytes':
				read_bytes=float(value_vlaue[6])
			if value_vlaue[0]=='write_bytes':
				write_bytes=float(value_vlaue[6])	
		cursor.execute('SELECT s_time,r_bytes,w_bytes from {} where c_name=?'.format(cur_table) ,(cur_client,))
		old_value = cursor.fetchall()
		if len(old_value)==0:
			flag=False # the first time to run this script.
			cursor.execute('insert into {} (c_name,s_time,r_bytes,w_bytes) values(?,?,?,?)'.format(cur_table),(cur_client,snapshot_time,read_bytes,write_bytes) )
			#print 'Insert new data %s' %cur_client
		else:
			old_value=old_value[0]
			read_rates = (read_bytes-old_value[1])/(snapshot_time-old_value[0])
			write_rates = (write_bytes-old_value[2])/(snapshot_time-old_value[0])
			cursor.execute('update {} set s_time=?,r_bytes=?,w_bytes=?,r_rates=?,w_rates=? where c_name=?'.format(cur_table),(snapshot_time,read_bytes,write_bytes,read_rates,write_rates,cur_client))
	conn.commit()
	if flag:
		cursor.execute('select c_name,r_rates,w_rates from {} order by w_rates desc'.format(cur_table))
		result = cursor.fetchall()[0:16]
		with open('{}.lg'.format(cur_OST),'a') as f:
			now = time.localtime()
			f.write('%d:%d:%d\n' %(now.tm_hour,now.tm_min,now.tm_sec))
			for r in result:
				f.write('./%s %s %s, ' %(r[0],r[2],r[1]))
			f.write('\n')
	cursor.close()
	conn.close()
if __name__ == '__main__':
	while  True:
		client_io()
		time.sleep(34)
	