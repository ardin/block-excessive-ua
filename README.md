# block-excessive-ua

**Follow log file and block excessive User-Agent in specified time**

```
$ ./block-excessive-ua.py -h
usage: block-excessive-ua.py [-h] [--allowed req] [--period sec] [--output file] [-v] log_file

Follow log file and block excessive User-Agent in specified time

positional arguments:
  log_file       LOG file

optional arguments:
  -h, --help     show this help message and exit
  --allowed req  allowed count one User-Agent (default 20 requests)
  --period sec   block if requests occurs in given period (default 10 seconds)
  --output file  output file contains detected blocked user agents (default /tmp/blocked-ua.vcl)
  -v             verbose mode
```

**Example output:**
```
$ ./block-excessive-ua.py --output /etc/varnish/blocked-ua.vcl /var/log/httpd/access.log 
2020-11-01 | 14:57:13 | INFO | BLOCK: Mozilla\/4.0 \(compatible; MSIE 8.0; Windows NT 5.1; Trident\/4.0; .NET CLR 2.0.50727; .NET4.0C; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; Core\/1.47.933.400a QQBrowser\/9.4.8699.400\
```

**Above involves blocking rule, which should be included in your varnish configuration:**
```
$ cat /etc/varnish/blocked-ua.vcl
# 2020-11-01 14:57:13
if (req.http.User-Agent ~ "Mozilla\/4.0 \(compatible; MSIE 8.0; Windows NT 5.1; Trident\/4.0; .NET CLR 2.0.50727; .NET4.0C; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; Core\/1.47.933.400a QQBrowser\/9.4.8699.400\)") { error 429 "Calm down."; }
```

**Example reload service:**
```
$ sudo cp systemd/* /usr/lib/systemd/system
$ sudo systemctl enable varnish-reloader.{path,service} 
$ sudo systemctl start varnish-reloader.{path,service}
```
