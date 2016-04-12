#监测每个客户端对OST的负载（io01）
## 依赖性
+ paramiko
```
pip install paramiko
```
+ futures
+ ```
pip install futures
```

##使用方法
```
$ ./create_multidb.py
$ ./monitor.sh
```
##说明
脚本每隔一分钟抓取每个客户端的读写数据，并计算读写速率。然后根据写速率进行排序，将（客户端，write_rates,read_rates）写入相应客户端的lg文件