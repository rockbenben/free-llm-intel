---
vendor: anyscale
title: 如何使用 Ray Tune 分布式调优超参数
original_title: How to distribute hyperparameter tuning using Ray Tune
url: https://anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune
date: 2022-02-15
lang: zh
captured: 2026-10-25
extractor: readability-v1
translator: agent
status: translated
body_sha: 2d49667de4ed
---

# 如何使用 Ray Tune 分布式调优超参数

作者：[Juan Navas](https://www.anyscale.com/blog?author=juan-navas) 与 [Richard Liaw](https://www.anyscale.com/blog?author=richard-liaw) | 2022 年 2 月 15 日

💡 *本文是超参数调优系列的第 3 篇。如果你才刚开始，请先读第 1 篇*[*什么是超参数调整？*](https://www.anyscale.com/blog/what-is-hyperparameter-tuning)*。在第 2 篇*[*如何在 XGBoost 上调整超参数*](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost)*里，我们做了一个动手实践的例子。*

在本系列三篇文章的第一篇里，我们了解了[超参数调优](https://www.anyscale.com/blog/what-is-hyperparameter-tuning)如何帮我们找到最优设置，让机器学习模型取得最好的结果。然后在第二篇里，我们学习了[如何在 XGBoost 上做超参数调优](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost)，并发现调优后的模型比未调优的模型预测更准确。

取决于搜索空间的大小，执行超参数调优的搜索算法可能要花很长时间，从几小时到几天不等。上一篇文章里我们跑随机搜索函数时，就看到了它在计算资源和时间上有多昂贵。

要想更快地调优超参数——同时不牺牲质量——我们就需要借助分布式计算，它让我们可以并行地尝试不同的超参数组合。

在本系列的最后一篇里，我们将演示如何用 [Ray Tune](https://anyscale.com/library/ray-tune) 库把超参数调优任务分发到多台计算机上。我们会演示如何用这套分布式机器学习工具，在本地的多个 CPU 上或在云端调优超参数。我们会继续优化数字识别模型，只不过这次把任务分出去，从而做得更快。

## 把超参数调优迁移到 Ray Tune

[Ray 项目](https://www.anyscale.com/ray-open-source)开发了 [tune-sklearn](https://github.com/ray-project/tune-sklearn)，作为 scikit-learn 的网格搜索和随机搜索超参数调优模型（分别是 GridSearchCV 和 RandomizedSearchCV）的直接替代品。它还支持其他搜索模型，比如贝叶斯搜索、树结构 Parzen 估计器等。你只需要把输入参数 **search_optimization** 设为 **bayesian** 或 **bohb**（对应贝叶斯优化），或设为 **hyperopt**（对应树结构 Parzen 估计器）。

tune-sklearn 还能无缝地与 Ray Tune 集成，在多台机器上做分布式超参数调优——无论本地还是云端——都不需要改动我们的代码。

这里，我们会改写[上一篇文章](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost)里写的代码，把 `RandomizedSearchCV()` 函数换成 `tune-sklearn`。

首先安装 tune-sklearn。在控制台命令行里，输入下面两条命令之一：

`$ pip install tune-sklearn "ray[tune]"`

或者：

`$ pip install -U git+https://github.com/ray-project/tune-sklearn.git && pip install 'ray[tune]'`

然后我们更新代码，把 `RandomizedSearchCV` 换成 `TuneSearchCV`。代码的最终版本如下，行内注释说明了所做的修改：

```
1import time
2import numpy as np
3import pandas as pd   # data processing, CSV file I/O (e.g. pd.read_csv)
4import xgboost as xgb
5
6from tune_sklearn import TuneSearchCV
7from sklearn import metrics
8
9# function to perform the tuning using tune-search library
10
11def tune_search_tuning():
12
13    # Input data files are available in the "./data/" directory.
14    train_df = pd.read_csv("./data/mnist_train_final.csv")
15    test_df = pd.read_csv("./data/mnist_test_final.csv")
16
17    # limit dataset size to 1000 samples
18    dataset_size = 1000
19    train_df = train_df.iloc[0:dataset_size, :]
20    test_df = test_df.iloc[0:dataset_size, :]
21
22    print("Reduced dataset size: ", train_df.shape)
23
24    y_train = train_df.label.values
25    x_train = train_df.drop('label', axis=1).values
26
27    y_test = test_df.label.values
28    x_test = test_df.drop('label', axis=1).values
29
30    params = {'max_depth': [6, 10],
31              'learning_rate': [0.1, 0.3, 0.4],
32              'subsample': [0.6, 0.7, 0.8, 0.9, 1],
33              'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1],
34              'colsample_bylevel': [0.6, 0.7, 0.8, 0.9, 1],
35              'n_estimators': [500, 1000],
36              'num_class': [10]
37              }
38
39    start_time = time.time()
40    print("starting at: ", start_time)
41
42    # define the booster classifier indicating the objective
43    # as multiclass "multi:softmax" and try to speed up execution
44    # by setting parameter tree_method = "hist"
45    xgbclf = xgb.XGBClassifier(objective="multi:softmax",
46                               tree_method="hist")
47
48    # replace RamdomizedSearchCV by TuneSearchCV
49    # n_trials sets the number of iterations (different hyperparameter combinations)
50    # that will be evaluated
51
52    # verbosity can be set from 0 to 3 (debug level).
53    tune_search = TuneSearchCV(estimator=xgbclf,
54                               param_distributions=params,
55                               scoring='accuracy',
56                               n_trials=20,
57                               n_jobs=8,
58                               verbose=2)
59
60    # perform hyperparameter tuning
61    tune_search.fit(x_train, y_train)
62
63    stop_time = time.time()
64    print("Stopping at :", stop_time)
65    print("Total elapsed time: ", stop_time - start_time)
66
67    best_combination = tune_search.best_params_
68
69    # evaluate accuracy based on the test dataset
70    predictions = tune_search.predict(x_test)
71
72    accuracy = metrics.accuracy_score(y_test, predictions)
73    print("Accuracy: ", accuracy)
74
75    return best_combination
76
77if __name__ == '__main__':
78
79    best_params = tune_search_tuning()
80    print("Best parameters:", best_params)
```

接下来，我们把上面的代码保存为 .py 文件，例如 **mnist_tune_search.py**。然后从控制台 CLI 运行这个文件：

`$ python mnist_tune_search.py `

Ray Tune 现在会根据我们计算机的架构（CPU 数量和每个 CPU 的核心数）并行启动若干进程（worker）来执行各轮评估。

把 `verbose` 设为 2 时，输出大致会是下面这样：

```
1Reduced dataset size:  (1000, 785)
2starting at:  1634516904.7016492
3== Status ==
4Memory usage on this node: 4.9/7.7 GiB
5Using FIFO scheduling algorithm.
6Resources requested: 2.0/12 CPUs, 0/0 GPUs, 0.0/2.54 GiB heap, 0.0/1.27 GiB objects
7Result logdir: /home/juan/ray_results/_Trainable_2021-10-18_02-28-34
8Number of trials: 16/20 (15 PENDING, 1 RUNNING)
9.
10.
11.
12Trial _Trainable_53eac_00019 reported average_test_score=0.85 with parameters={'early_stopping': False, 'early_stop_type': <EarlyStopping.NO_EARLY_STOP: 7>, 'X_id': ObjectRef(ffffffffffffffffffffffffffffffffffffffff0100000001000000), 'y_id': ObjectRef(ffffffffffffffffffffffffffffffffffffffff0100000002000000), 'groups': None, 'cv': StratifiedKFold(n_splits=5, random_state=None, shuffle=False), 'fit_params': {}, 'scoring': {'score': make_scorer(accuracy_score)}, 'max_iters': 1, 'return_train_score': False, 'n_jobs': 1, 'metric_name': 'average_test_score', 'max_depth': 10, 'learning_rate': 0.4, 'subsample': 1.0, 'colsample_bytree': 0.8, 'colsample_bylevel': 0.8, 'n_estimators': 1000, 'num_class': 10, 'estimator_ids': [ObjectRef(ffffffffffffffffffffffffffffffffffffffff0100000003000000)]}. This trial completed.
13== Status ==
14Memory usage on this node: 4.7/7.7 GiB
15Using FIFO scheduling algorithm.
16Resources requested: 0/12 CPUs, 0/0 GPUs, 0.0/2.54 GiB heap, 0.0/1.27 GiB objects
17Current best trial: 53eac_00016 with average_test_score=0.869 and parameters={'max_depth': 10, 'learning_rate': 0.3, 'subsample': 0.9, 'colsample_bytree': 0.7, 'colsample_bylevel': 0.6, 'n_estimators': 500, 'num_class': 10}
18Result logdir: /home/juan/ray_results/_Trainable_2021-10-18_02-28-34
19Number of trials: 20/20 (20 TERMINATED)
20
21+------------------------+------------+-------+---------------------+--------------------+-----------------+-------------+----------------+-------------+-------------+--------+------------------+---------------------+---------------------+---------------------+
22| Trial name             | status     | loc   |   colsample_bylevel |   colsample_bytree |   learning_rate |   max_depth |   n_estimators |   num_class |   subsample |   iter |   total time (s) |   split0_test_score |   split1_test_score |   split2_test_score |
23|------------------------+------------+-------+---------------------+--------------------+-----------------+-------------+----------------+-------------+-------------+--------+------------------+---------------------+---------------------+---------------------|
24| _Trainable_53eac_00000 | TERMINATED |       |                 0.6 |                0.7 |             0.4 |           6 |            500 |          10 |         0.6 |      1 |          116.009 |               0.855 |               0.865 |               0.86  |
25| _Trainable_53eac_00001 | TERMINATED |       |                 0.6 |                0.8 |             0.4 |          10 |            500 |          10 |         0.7 |      1 |          122.63  |               0.865 |               0.845 |               0.875 |
26| _Trainable_53eac_00002 | TERMINATED |       |                 1   |                0.6 |             0.1 |           6 |           1000 |          10 |         0.7 |      1 |          300.112 |               0.87  |               0.865 |               0.885 |
27| _Trainable_53eac_00003 | TERMINATED |       |                 1   |                1   |             0.4 |          10 |            500 |          10 |         0.6 |      1 |          132.811 |               0.87  |               0.875 |               0.85  |
28| _Trainable_53eac_00004 | TERMINATED |       |                 0.9 |                0.6 |             0.4 |           6 |           1000 |          10 |         0.8 |      1 |          227.973 |               0.85  |               0.865 |               0.855 |
29| _Trainable_53eac_00005 | TERMINATED |       |                 0.8 |                0.9 |             0.1 |          10 |           1000 |          10 |         0.6 |      1 |          310.683 |               0.85  |               0.88  |               0.875 |
30| _Trainable_53eac_00006 | TERMINATED |       |                 0.8 |                0.9 |             0.3 |           6 |           1000 |          10 |         0.8 |      1 |          250.689 |               0.865 |               0.865 |               0.86  |
31| _Trainable_53eac_00007 | TERMINATED |       |                 0.6 |                1   |             0.4 |           6 |            500 |          10 |         0.9 |      1 |          132.995 |               0.86  |               0.87  |               0.88  |
32| _Trainable_53eac_00008 | TERMINATED |       |                 1   |                0.9 |             0.4 |           6 |            500 |          10 |         0.8 |      1 |          139.673 |               0.85  |               0.86  |               0.845 |
33| _Trainable_53eac_00009 | TERMINATED |       |                 0.7 |                0.9 |             0.3 |           6 |            500 |          10 |         0.8 |      1 |          142.673 |               0.89  |               0.88  |               0.86  |
34| _Trainable_53eac_00010 | TERMINATED |       |                 1   |                0.6 |             0.1 |           6 |            500 |          10 |         0.7 |      1 |          198.696 |               0.87  |               0.865 |               0.885 |
35| _Trainable_53eac_00011 | TERMINATED |       |                 0.7 |                0.7 |             0.4 |          10 |            500 |          10 |         1   |      1 |          135.517 |               0.875 |               0.875 |               0.865 |
36| _Trainable_53eac_00012 | TERMINATED |       |                 0.8 |                0.8 |             0.3 |           6 |            500 |          10 |         1   |      1 |          154.802 |               0.865 |               0.865 |               0.895 |
37| _Trainable_53eac_00013 | TERMINATED |       |                 0.7 |                0.8 |             0.3 |           6 |            500 |          10 |         0.8 |      1 |          140.004 |               0.87  |               0.87  |               0.88  |
38| _Trainable_53eac_00014 | TERMINATED |       |                 0.8 |                0.6 |             0.3 |          10 |           1000 |          10 |         0.8 |      1 |          232.962 |               0.85  |               0.87  |               0.89  |
39| _Trainable_53eac_00015 | TERMINATED |       |                 0.7 |                1   |             0.1 |           6 |            500 |          10 |         0.8 |      1 |          216.729 |               0.86  |               0.895 |               0.87  |
40| _Trainable_53eac_00016 | TERMINATED |       |                 0.6 |                0.7 |             0.3 |          10 |            500 |          10 |         0.9 |      1 |          136.364 |               0.87  |               0.88  |               0.88  |
41| _Trainable_53eac_00017 | TERMINATED |       |                 0.6 |                1   |             0.4 |           6 |            500 |          10 |         0.7 |      1 |          123.14  |               0.86  |               0.855 |               0.855 |
42| _Trainable_53eac_00018 | TERMINATED |       |                 0.9 |                0.8 |             0.3 |           6 |            500 |          10 |         0.6 |      1 |          133.816 |               0.84  |               0.865 |               0.875 |
43| _Trainable_53eac_00019 | TERMINATED |       |                 0.8 |                0.8 |             0.4 |          10 |           1000 |          10 |         1   |      1 |          239.038 |               0.855 |               0.87  |               0.85  |
44+------------------------+------------+-------+---------------------+--------------------+-----------------+-------------+----------------+-------------+-------------+--------+------------------+---------------------+---------------------+---------------------+
45
46Stopping at : 1634517645.9786417
47Total elapsed time:  741.276992559433
48Accuracy:  0.848
49Best parameters: {'max_depth': 10, 'learning_rate': 0.3, 'subsample': 0.9, 'colsample_bytree': 0.7, 'colsample_bylevel': 0.6, 'n_estimators': 500, 'num_class': 10}
```

这个过程花了 12 分钟多，它找到了最佳的超参数组合，把准确率提高到 84.8%（上一篇文章里用默认超参数值时是 82.6%）。

## 分布式执行超参数调优

接下来，我们把超参数调优的负载分摊到多台计算机上。我们会用 [Ray](https://www.ray.io/) 来做分布式调优。我们要搭一个由头节点和一组工作节点组成的 Ray 集群。需要先启动头节点，然后让工作节点连上去。

![blog-distrubuted-hyperparameter-tuning-processing](https://images.ctfassets.net/xjan103pcp94/4BkQcFkzVe4ZYUrov8NzZ3/ceeea98bfc3feca6b43ef52168defdff/blog-distrubuted-hyperparameter-tuning-processing.png)

blog-distrubuted-hyperparameter-tuning-processing

首先，我们需要安装 Ray 模块。在控制台 CLI 里输入下面的命令：

`$ pip install ray`

请注意，本次练习中，参与集群的所有节点必须保证环境完全一致，这一点非常关键。要特别留意 Ray 和 XGBoost 的版本。本教程中的代码是在以下版本上测试的：

```
1$ pip show ray 
2Name: ray
3Version: 1.7.0
4
5$ pip show xgboost
6Name: xgboost
7Version: 1.2.0
```

接下来，我们对之前的函数做以下调整：

- 把数据文件复制到 Ray 集群中所有节点的同一个目录下。使用诸如 `/var/data` 的绝对路径。
- 导入 Ray 库。
- 初始化 Ray 以连接本地节点：`ray.init(address='auto')`。
- 在函数声明前用 @ray.remote 把 `tune_search_tuning()` 装饰成 Ray 任务。
- 把数据文件的完整路径更新为它们被复制到的位置。例如：`/var/data/mnist_train_final.csv`
- 在主函数中加入 worker 的创建与处理。
- 把计时器移到主函数。

新代码如下，改动已在行内注释中标出：

```
1import time
2import numpy as np
3import pandas as pd   # data processing, CSV file I/O (e.g. pd.read_csv)
4import xgboost as xgb
5
6from tune_sklearn import TuneSearchCV
7from sklearn.model_selection import train_test_split
8from sklearn import metrics
9import ray
10
11# init ray and attach it to local node ray instance
12ray.init(address='auto')
13
14# function to perform the tuning using tune-search library
15# add function decorator
16@ray.remote
17def tune_search_tuning():
18
19    # Input data files are available in the "/var/data/" directory.
20    train_df = pd.read_csv("/var/data/mnist_train_final.csv")
21    test_df = pd.read_csv("/var/data/mnist_test_final.csv")
22    print (train_df.shape, test_df.shape)
23
24    dataset_size = 1000
25    train_df = train_df.iloc[0:dataset_size, :]
26    test_df = test_df.iloc[0:dataset_size, :]
27
28    y = train_df.label.values
29    x = train_df.drop('label', axis=1).values
30
31    y_test = test_df.label.values
32    x_test = test_df.drop('label', axis=1).values
33
34    # define the train set and test set
35    # in principle the test (valid) data is not used later, 
36    # so we minimize the size to just 5%.
37    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.05)
38    print("Shapes - X_train: ", x_train.shape, ", X_val: ", x_val.shape, ", y_train: ", y_train.shape, ", y_val: ", y_val.shape)
39
40    # numpy arrays are not accepted in params attributes, 
41    # so we use python comprehension notation to build lists
42    params = {'max_depth': [3, 6, 10, 15],
43              'learning_rate': [0.01, 0.1, 0.2, 0.3, 0.4],
44              'subsample': [0.5 + x / 100 for x in range(10, 50, 10)],
45              'colsample_bytree': [0.5 + x / 100 for x in range(10, 50, 10)],
46              'colsample_bylevel': [0.5 + x / 100 for x in range(10, 50, 10)],
47              'n_estimators': [100, 500, 1000],
48              'num_class': [10]
49              }
50
51    # define the booster classifier indicating the objective as 
52    # multiclass "multi:softmax" and try to speed up execution
53    # by setting parameter tree_method = "hist"
54    xgbclf = xgb.XGBClassifier(objective="multi:softmax",
55                               tree_method="hist")
56
57    # replace RamdomizedSearchCV by TuneSearchCV
58    # n_trials sets the number of iterations (different hyperparameter combinations)
59    # that will be evaluated
60    # verbosity can be set from 0 to 3 (debug level).
61    tune_search = TuneSearchCV(estimator=xgbclf,
62                               param_distributions=params,
63                               scoring='accuracy',
64                               n_trials=25,
65                               verbose=1)
66
67    # perform hyperparameter tuning
68    tune_search.fit(x_train, y_train)
69
70    print("cv results: ", tune_search.cv_results_)
71
72    best_combination = tune_search.best_params_
73    print("Best parameters:", best_combination)
74
75    # evaluate accuracy based on the test dataset
76    predictions = tune_search.predict(x_test)
77
78    accuracy = metrics.accuracy_score(y_test, predictions)
79    print("Accuracy: ", accuracy)
80
81    return best_combination
82
83if __name__ == '__main__':
84
85    start_time = time.time()
86
87    # create the task
88    remote_clf = tune_search_tuning.remote()
89
90    # get the task result
91    best_params = ray.get(remote_clf)
92
93    stop_time = time.time()
94    print("Stopping at :", stop_time)
95    print("Total elapsed time: ", stop_time - start_time)
96
97    print("Best params from main function: ", best_params)
```

把上面的代码保存到一个文件，例如 **mnist_ray_tune_distributed.py**。

在运行上面的代码之前，你需要先启动一个 Ray 集群。[Ray Cluster Overview](https://docs.ray.io/en/latest/cluster/index.html) 文档里有详尽的说明。这份文档会展示如何在任何云提供商上启动 Ray 集群，其中包含关于 AWS、GCP、Azure 等主流云厂商的详细信息。不过，你也可以在本地自建环境里跑 Ray 集群，只要在不同的服务器上分别启动头节点和各个 worker。

在本地搭建 Ray 集群的一个简单办法是：从命令行手动启动头节点，再把 worker 挂上去：

```
1$ ray start --head --port=6379 
2Local node IP: 192.168.0.196
32021-10-19 23:38:33,209	INFO services.py:1252 -- View the Ray dashboard at http://127.0.0.1:8265
4
5--------------------
6Ray runtime started.
7--------------------
8
9Next steps
10  To connect to this Ray runtime from another node, run
11    ray start --address='192.168.0.196:6379' --redis-password='5241590000000000'
12
13  Alternatively, use the following Python code:
14    import ray
15    ray.init(address='auto', _redis_password='5241590000000000')
16
17  To connect to this Ray runtime from outside of the cluster, for example to
18  connect to a remote cluster from your laptop directly, use the following
19  Python code:
20    import ray
21    ray.init(address='ray://<head_node_ip_address>:10001')
22
23  If connection fails, check your firewall settings and network configuration.
```

头节点已经跑起来了，现在我们可以用 `ray start --head` 命令给出的 Redis 密码来连接工作节点。在 Ray 集群的其他节点上，在命令行里输入下面的命令，并把 IP 地址替换成你环境里实际头节点的地址：

`$ ray start --address='192.168.0.196:6379' --redis-password='5241590000000000'`

Ray 集群跑起来之后，我们只需要在其中一个节点上运行 Python 脚本。在本次练习中，我们搭了一个两节点的 Ray 集群。在其中一个节点上，我们在命令行里输入：

`$ python mnist_ray_tune_distributed.py`

我们预期输出大致如下：

```
1INFO worker.py:827 -- Connecting to existing Ray cluster at address: 192.168.0.196:6379
2.
3. 
4. 
5Accuracy:  0.82
6Total elapsed time:  315.5932471752167
7Best params from main function:  {'max_depth': 3, 'learning_rate': 0.1, 'subsample': 0.9, 'colsample_bytree': 0.6, 'colsample_bylevel': 0.9, 'n_estimators': 1000, 'num_class': 10}
```

这次测试跑了 315 秒（约 5 分钟）。这不到上一次测试耗时的一半——那次 Python 脚本跑在单个节点上，用了 741 秒。另外，新测试中最佳超参数组合的准确率是 82.0%，与我们之前用 scikit-learn 的 RandomizedSearchCV 函数得到的结果相近（85.8%）。

把超参数调优分散到集群上跑，比在单台计算机上快得多。虽然结果与 scikit-learn 几乎一样，但通过把工作分摊出去，我们更快地拿到了这些结果。

## 后续步骤

[Ray Tune](https://anyscale.com/library/ray-tune) 让自动化并在多台机器的多个节点上分布式执行超参数调优变得很容易，无论本地还是云端。

如我们所见，用 Ray Tune 的 TuneSearchCV 替换 scikit-learn 的 RandomizedSearchCV，再跑在 Ray 集群上，让我们能轻松地把超参数调优过程分散到多个节点。这最多能把调优所需的时间缩短到 1/N——N 是你的 Ray 集群中的节点数——因为分布式计算总会有一些开销。

如果你想快速调优模型的超参数，不妨试试 Ray 和 [Ray Tune](https://docs.ray.io/en/latest/tune/index.html) 来改进你自己的模型——如果你想用 Ray 但又不想自己管理和扩缩集群，可以[注册 Anyscale](https://www.anyscale.com/beta)。
