# 使用 Gunicorn、Nginx 和 HTTPS 安全地部署 Django 应用程序

---

> https://realpython.com/django-nginx-gunicorn/#replacing-wsgiserver-with-gunicorn

# 项目安装启动

```bash
# 安装依赖
$ pip install -r requirements.txt

# 项目校验
$ python manage.py check

# 前台启动
$ python manage.py runserver

# 后台启动
$ nohup python manage.py runserver &
[1] 12441
nohup: 忽略输入并把输出追加到'nohup.out'

$ jobs -l
[1]  + 12441 running    nohup python manage.py runserver

$ sudo lsof -n -P -i TCP:8000 -s TCP:LISTEN
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python  12452 mark    4u  IPv4 145236      0t0  TCP 127.0.0.1:8000 (LISTEN)
```

# Gunicorn 安装

```bash
$ pip install gunicorn
$ gunicorn -c config/gunicorn/dev.py
$ killall gunicorn
```

# Nginx 安装

> http://nginx.org/en/download.html

- 下载 & 解压

```bash
$ wget http://nginx.org/download/nginx-1.20.2.tar.gz
$ tar -zxvf nginx-1.20.2.tar.gz 
```

- 依赖安装

```bash
$ sudo apt-get install build-essential
$ sudo apt-get install libtool
$ sudo apt-get install libpcre3 libpcre3-dev
$ sudo apt-get install zlib1g-dev
$ sudo apt-get install openssl
$ sudo apt-get install libssl-dev
```

- 编译 & 安装

```bash
$ cd nginx-1.20.2/
$ ./configure --prefix=/usr/local/nginx --with-http_ssl_module --with-http_stub_status_module
$ make
$ make install # 根据 configure 参数进行安装，默认安装在 /usr/local/nginx 目录下
```

- 建立一个软连接，方便启动

```bash
$ ln -s /usr/local/nginx/sbin/nginx /usr/local/bin/nginx
```

- 启动 & 停止 & 热更新

```bash
$ nginx
$ nginx -s stop
$ nginx -s reload
```

- 使用 vim 修改配置支持语法高亮

```bash
$ cp -r nginx-1.20.2/contrib/vim/* ~/.vim/
```

- 配置

```conf
server {
    if ($host = example.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen       80;
    server_name  example.com;
    return 404; # managed by Certbot
}

server {
        server_name  example.com;

        #charset koi8-r;

        access_log  logs/host.access.log  main;

        location / {
            root   /var/www/frontend;
            index  index.html index.htm;
        }

        location /api {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        error_page  404              /404.html;

        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
        
        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```

# Let's Encrypt 证书配置

> https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/
> http://nginx.org/en/docs/http/configuring_https_servers.html

- 安装依赖

```bash
$ apt-get update
$ sudo apt-get install certbot
$ apt-get install python3-certbot-nginx
```

- 申请证书的域名

1. `--nginx-server-root` 用于指定 nginx conf 配置目录，默认要求是 `/etc/nginx/nginx.conf`，所以这里需要手动指定
2. 执行下面命令的时候，最好把 `nginx.conf` 文件中的 server_name 更改为对应域名，这样在生成证书时方便程序自己做配置

```bash
$ $ sudo certbot --nginx --nginx-server-root=/usr/local/nginx/conf -d console.bytefun.link --register-unsafely-without-email
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator nginx, Installer nginx
Registering without email!

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at
https://letsencrypt.org/documents/LE-SA-v1.2-November-15-2017.pdf. You must
agree in order to register with the ACME server at
https://acme-v02.api.letsencrypt.org/directory
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(A)gree/(C)ancel: A
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for console.bytefun.link
Waiting for verification...
Cleaning up challenges
Deploying Certificate to VirtualHost /usr/local/nginx/conf/nginx.conf

Please choose whether or not to redirect HTTP traffic to HTTPS, removing HTTP access.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
1: No redirect - Make no further changes to the webserver configuration.
2: Redirect - Make all requests redirect to secure HTTPS access. Choose this for
new sites, or if you're confident your site works on HTTPS. You can undo this
change by editing your web server's configuration.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
Redirecting all traffic on port 80 to ssl in /usr/local/nginx/conf/nginx.conf

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations! You have successfully enabled https://console.bytefun.link

You should test your configuration at:
https://www.ssllabs.com/ssltest/analyze.html?d=console.bytefun.link
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/console.bytefun.link/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/console.bytefun.link/privkey.pem
   Your cert will expire on 2022-03-14. To obtain a new or tweaked
   version of this certificate in the future, simply run certbot again
   with the "certonly" option. To non-interactively renew *all* of
   your certificates, run "certbot renew"
 - Your account credentials have been saved in your Certbot
   configuration directory at /etc/letsencrypt. You should make a
   secure backup of this folder now. This configuration directory will
   also contain certificates and private keys obtained by Certbot so
   making regular backups of this folder is ideal.
 - If you like Certbot, please consider supporting our work by:

   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
   Donating to EFF:                    https://eff.org/donate-le
```

- 配置证书自动更新

```bash
$ crontab -e
0 12 * * * /usr/bin/certbot renew --quiet

# 上面定时任务表示，每天中午运行命令。该命令检查服务器上的证书是否会在接下来的 30 天内过期，如果是，则更新它。--quiet 指令表示 certbot 不要生成输出
```

