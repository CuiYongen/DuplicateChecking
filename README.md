# DuplicateChecking
基于 Simhash 的论文查重系统

## 项目背景
**本项目为论文内查系统，即需要自行准备论文库**

```
远古时期的本科毕设项目，时至今日看到偶尔有人 star

全靠回忆写点 readme，希望尽可能有一些帮助

当时导师需求为：

一些学生抄袭往届学长学姐论文（特别是同专业的）

由于特殊原因，本校论文不会及时纳入知网查重库（但导师手里有，原因不详）

故开发此项目
```

## 部署
``` bash
cd D:\duplicateChecking\Flask //进入项目目录
venv\Scripts\activate //激活虚拟环境
python start.py //启动项目
```

* 项目运行所需的包已经安装在虚拟环境中，理论上可直接运行
* 如需直接部署（**不建议**）请自行根据提示安装
* 项目基于 MongoDB，确保服务已运行

## 启动
1. 在 `start.py` 中设置
``` python
app.run(host='127.0.0.1', port=5000, debug=True) //设置地址并开启调试模式
```
2. 网页进入 `127.0.0.1:5000 //上述设置地址`

<img width="427" alt="image" src="https://user-images.githubusercontent.com/12591929/162346362-f1c84f30-131e-4c55-8821-9aa3e78ce5b2.png">

## 使用
**顺序操作即可**
* 文件上传没有可视化界面可能造成困扰：待上传的文件选中完毕后，点击`上传`即可
* 论文库上传后存放在 `/docs/lib`
* 待查重论文上传后存放在 `/docs/check`
* 论文库的任何改动，都需要重新 `点击开始初始化`
* `点击查看结果` 只显示最后一篇的查询结果（做了点UI）
* 可以一次查询多篇论文，结果以 txt 形式保存在 `/result` 中


## 其他说明
**项目核心为三个模块，，`dupl_ckg`，`flk_mdb`, `web_mod`**
* `dupl_ckg` 为查重模块，即 Simhash 算法
* `flk_mdb` 为[轻量化 MongoDB ORM 库](https://github.com/Pingze-github/mango/blob/master/mango.py)
* `web_mod` 为网页操作模块，如上传等
* `/app/routes.py` 为路由规则
* `/app/templates` 包含网页模板
```
可以看出，本项目缺陷明显，可改进空间巨大

但项目本身有一定实用意义（服务导师，揭穿部分同学的不法行为）

此处向曾经因为没有 readme 产生困扰的同学们诚挚道歉（虽然写了好像也没啥用）
```
