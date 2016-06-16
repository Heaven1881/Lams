# Lams
Learning Analysis Manager System(LAMS)，用于在操作系统课程OpenEdx平台下收集分析学生行为

## 部署方法
### 独立部署
需要依赖的环境:
- Python 2.7
- Nginx：这是整个系统运行的基础，系统通过Nginx向外提供服务。
- php-fpm：处理一些数据筛选，这个不是必须的，但是一些特殊的展现结果(例如个人章节得分排名)需要php-fpm的支持。

> php-fpm负责提供php脚本的执行，一般来说不需要单独安装，`php 7.0`已经包含了`php-fpm`，对应安装方法参考这个链接：http://php.net/manual/en/install.php

只需要将代码部署到服务器的任意位置即可，其对应的Nginx配置可以参考文件`lams-nginx.conf`。

```bash
$ git clone https://github.com/Heaven1881/Lams.git
```

在完成代码的部署之后，你需要修改对应的配置文件，包括：
- 根目录下的`conf.py`，是系统整体配置
- collector子目录的所有`config.py`是各个Collector的配置

### 以扩展的方式部署到Open edX上
需要依赖的内容和独立部署一样，不过因为Open edX本身就依赖于Open edX，因此需要安装的只有php-fpm。

克隆代码

```bash
$ cd /
$ git clone https://github.com/Heaven1881/Lams.git
```

在Open edX的static文件目录中创建指向数据目录和展现目录的软连接

```bash
$ cd /edx/var/edxapp/staticfiles
$ mkdir lams
$ ln -s /Lams/var stat
$ ln -s /Lams/visual view
```

**配置Open edX**
使用vim或任意编辑器打开`/edx/app/nginx/sites-available/cms`，找到如下代码：
```nginx
# return a 403 for static files that shouldn't be
# in the staticfiles directory
location ~ ^/static/(?:.*)(?:\.xml|\.json|README.TXT) {
  return 403;
}
```
改为如下：
```nginx
location ~ ^/static/(?:.*)(?:\.xml|README.TXT) {
  return 403;
}
```
这样的修改是为了去除对*.json文件的限制，因为系统的数据基本上保存在*.json文件里面。

在下方添加如下代码，增加Open edX的staticfiles对php脚本的支持。

```nginx
location ~* \.php$ {
  fastcgi_pass    127.0.0.1:9000;
  include         fastcgi_params;
  fastcgi_param   SCRIPT_FILENAME    $document_root/staticfiles/$file;
  fastcgi_param   SCRIPT_NAME        $fastcgi_script_name;
}
```

重启Open edX

```bash
$ sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:
$ sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp_worker:
```

在完成代码的部署之后，你需要修改对应的配置文件，包括：
- 根目录下的`conf.py`，是系统整体配置
- collector子目录的所有`config.py`是各个Collector的配置

## 使用方法
**数据收集**
使用如下命令触发所有收集者的工作

```bash
$ sh /Lams/collector/collect-all.sh
```

完成收集后，收集到的数据会保存到`/Lams/datapool/new`中。

**数据分析**
使用如下代码完成数据的处理工作

```bash
$ python /Lams/lams.py
```
完成处理后，结果保存在`/Lams/var`目录中，处理日志在`/Lams/log`目录中。
数据的收集和分析均支持增量操作。
