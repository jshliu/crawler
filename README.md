## 概述
该项目是一个基于 **python** 的爬虫框架。

## 环境要求

* 操作系统: 类`unix`系统均可，windows下爬虫任务调度无法正常运行
* python: `2.7`
* pip: `最新稳定版`
* redis: `最新稳定版`
* mysql: `5.7`

## 开始
首先进入项目根目录。

1. 安装依赖。

    > pip install -r requirements.txt

2. 更改配置项。
  
    配置文件地址：`/crawler/settings/conf/core-site.xml`

    1. 修改 `mysql`、`redis` 配置。

        mysql：`mysql.host`、`mysql.port`、`mysql.user`、`mysql.password`、`mysql.db`、`mysql.charset`

        redis：`redis.host`、`redis.port`、`redis.db`

    2. 修改日志存放位置 `log.dir`。

    3. 修改爬虫任务相关进程id文件存放地址`task.pid`、`job.pid`。

3. 初始化数据库。

    利用 django 框架的 migrate 功能。

    > python ./manage.py migrate

3. 启动/停止爬虫。

    > python ./manage.py runscript main --script-args=start

    `--script-args` 可以指定爬虫启动（`start`）/停止（`stop`）

## 开发

### 目录结构简介
```
|-- crawler
   |-- apps # 存放数据模型以及migration
   |-- context # python 动态导入相关实现
   |-- file # 一些数据文件
   |-- scripts # 脚本存放目录
   |-- service # 爬虫框架实现
      |-- crawlerimpl # 具体爬虫实现，比如爬取网易buff 交易数据就可以作为其中一个实现
      |-- models # 具体爬虫所用到的数据模型，目前也许暂时不用
      |-- scheduler # 爬虫任务调度相关实现
   |-- settings # 系统配置相关文件
|-- manage.py # django 入口文件，启动项目、执行数据迁移都会用到
|-- requirements.txt # 项目依赖申明，可用pip直接完成依赖安装

```

### 开发一个爬虫实现

可参考 `service/crawlerimpl/accessory/buff.py`，该文件可直接使用 python 当作脚本执行，而不需要启动整个爬虫框架。
