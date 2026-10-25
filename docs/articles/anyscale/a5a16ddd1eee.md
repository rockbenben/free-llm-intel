---
vendor: anyscale
title: 如何使用 Ray Tune 分配超参数调整
original_title: 
url: https://anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune
date: 2022-02-15
lang: zh
captured: 2026-10-25
extractor: readability-v1
translator: mt
status: translated
body_sha: 9d7cc2f9d335
---

[主页](https://www.anyscale.com/)[博客](https://www.anyscale.com/blog)博客详细信息

# 如何使用 Ray Tune 分配超参数调整

作者：[Juan Navas](https://www.anyscale.com/blog?author=juan-navas) 和 [Richard Liaw](https://www.anyscale.com/blog?author=richard-liaw) | 2022 年 2 月 15 日

💡 *这篇博文是我们超参数调优系列的第 3 部分。如果您刚刚开始，请查看第 1 部分，*[*什么是超参数调整？*](https://www.anyscale.com/blog/what-is-hyperparameter-tuning)*。在第 2 部分，*[*如何调整 XGBoost 上的超参数*](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost)*，我们探索了一个实用的实践示例。*

在我们的三部分系列的第一篇文章中，我们了解了[调整超参数](https://www.anyscale.com/blog/what-is-hyperparameter-tuning)如何帮助我们的机器学习模型找到最佳结果的最佳设置。然后，在第二篇文章中，我们学习了[如何在 XGBoost 上执行超参数调整](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost)，并发现我们调整的模型比未调整的模型做出更准确的预测。

根据搜索空间的不同，执行超参数调整的搜索算法可能需要很长时间，从几小时到几天不等。当我们运行上一篇文章中的随机搜索功能时，我们看到了它在计算资源和时间上的成本有多么高。

为了在不影响质量的情况下更快地调整超参数，我们需要采用分布式计算，这使我们能够并行尝试不同的超参数组合。

在本系列的最后一篇文章中，我们将演示如何使用 Ray Tune(https://anyscale.com/library/ray-tune) 库在多台计算机之间分配超参数调整任务。我们将演示如何使用分布式机器学习工具包来调整多个本地 CPU 或云中的超参数。我们将继续优化我们的数字识别模型，但我们会通过分配任务来更快地完成它。

## LinkPorting 超参数调整到 Ray Tune

[Ray 项目](https://www.anyscale.com/ray-open-source) 开发了 [tune-sklearn](https://github.com/ray-project/tune-sklearn)，分别作为 scikit-learn 的网格搜索和随机搜索超参数调整模型 GridSearchCV 和 RandomizedSearchCV 的直接替代品。它还支持其他搜索模型，例如贝叶斯搜索、树结构 Parzen 估计器等。只需将输入参数 **search_optimization** 设置为 **bayesian** 或 **bohb**（用于贝叶斯优化），或设置 **hyperopt**（用于树结构 Parzen 估计器）即可。

Tune-sklearn 还与 Ray Tune 无缝集成，可在本地或云端的多台机器上进行分布式超参数调整，而无需更改我们的代码。

在这里，我们将调整我们在[上一篇文章](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost)中编写的代码，以用“tune-sklearn”替换“RandomizedSearchCV()”函数。

首先，我们安装tune-sklearn。在控制台命令行中，我们键入以下内容之一：

`$ pip installune-sklearn "ray[tune]"`

或者：

`$ pip install -U git+https://github.com/ray-project/tune-sklearn.git && pip install 'ray[tune]'`

然后，我们更新代码，将“RandomizedSearchCV”替换为“TuneSearchCV”。代码的最终版本如下，内嵌注释解释了修改内容：
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
接下来，我们将上面的代码保存在 .py 文件中。例如，**mnist_tune_search.py​​*。然后我们从控制台 CLI 运行此文件：

`$ python mnist_tune_search.py`

Ray Tune 现在根据我们的计算机架构（CPU 数量和每个 CPU 的核心数量）并行启动多个进程（工作进程）来执行评估迭代。

将“verbose”设置为 2 时，我们可以预期输出类似于以下文本：
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
该过程花费了 12 分钟多的时间，并找到了最佳的超参数组合，可将准确度提高到 84.8%（如上一篇文章所示，默认超参数值的准确度为 82.6%）。

## LinkDistributing超参数调优处理

接下来，我们将在多台计算机之间分配超参数调整负载。我们将使用 [Ray](https://www.ray.io/) 分发我们的调整。我们将构建一个包含一个头节点和一组工作节点的 Ray 集群。我们需要首先启动头节点。然后工作人员连接到它。

![blog-distrubuted-hyperparameter-tuning-processing](https://images.ctfassets.net/xjan103pcp94/4BkQcFkzVe4ZYUrov8NzZ3/ceeea98bfc3feca6b43ef52168defdff/blog-distrubuted-hyperparameter-tuning-processing.png)

博客分布式超参数调整处理

首先，我们需要安装 Ray 模块。在控制台 CLI 中，我们输入以下命令：

`$ pip 安装 ray`

请注意，对于此练习，确保参与集群的所有节点上的环境完全相同至关重要。密切关注Ray和XGBoost的版本。我们已在以下版本上测试了本教程中的代码：
```
1$ pip show ray 
2Name: ray
3Version: 1.7.0
4
5$ pip show xgboost
6Name: xgboost
7Version: 1.2.0
```
接下来，我们对之前的函数进行以下调整：

- 将数据文件复制到 Ray 集群中所有节点的同一目录。使用绝对路径，例如“/var/data”。
- 导入射线库。
- 初始化 Ray 连接到本地节点，`ray.init(address='auto')`。
- 在函数声明之前使用 @ray.remote 将函数 `tune_search_tuning()` 装饰为 Ray 任务。
- 更新数据文件的完整路径以与其复制的位置相对应。例如：`/var/data/mnist_train_final.csv`
- 将worker的创建和处理添加到主函数中。
- 将计时器移至主功能。

新代码如下，其中内嵌注释了更改：
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
将上面的代码保存在文件中，例如 **mnist_ray_tune_distributed.py**。

在运行上面的代码之前，您需要启动一个Ray集群。 [Ray Cluster 概述](https://docs.ray.io/en/latest/cluster/index.html) 文档中提供了丰富的文档。本文档将向您展示如何在任何云提供商上启动 Ray 集群。它包含有关 AWS、GCP 和 Azure 等流行云提供商的详细信息。但是，您还可以通过启动不同服务器上的头节点和工作线程来在本地运行 ray 集群。

在本地设置 Ray 集群的一种简单方法是手动启动头节点并从命令行将工作节点附加到它：
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
现在头节点正在运行，我们可以使用“ray start --head”命令提供的 Redis 密码连接工作节点。在 Ray 集群中的其余节点上，在命令行中输入以下内容，将 IP 地址替换为环境中实际头节点的 IP 地址：

`$ ray start --address='192.168.0.196:6379' --redis-password='5241590000000000'`

Ray 集群运行后，我们只需在其中一个节点上运行 Python 脚本即可。在当前练习中，我们设置了一个包含两个节点的 Ray 集群。在其中一个节点，我们在命令行中输入以下内容：

`$ python mnist_ray_tune_distributed.py`

我们期望这样的输出：
```
1INFO worker.py:827 -- Connecting to existing Ray cluster at address: 192.168.0.196:6379
2.
3. 
4. 
5Accuracy:  0.82
6Total elapsed time:  315.5932471752167
7Best params from main function:  {'max_depth': 3, 'learning_rate': 0.1, 'subsample': 0.9, 'colsample_bytree': 0.6, 'colsample_bylevel': 0.9, 'n_estimators': 1000, 'num_class': 10}
```
测试运行时间为 315 秒（约 5 分钟）。这还不到上次测试时间的一半，上次测试的 Python 脚本在单个节点上运行，耗时 741 秒。此外，对于最佳超参数组合，新测试的准确率为 82.0%，与我们之前使用 scikit-learn RandomizedSearchCV 函数获得的结果 (85.8%) 类似。

在集群中分布超参数调整的运行速度比在单台计算机上快得多。尽管我们的结果实际上与 scikit-learn 相同，但我们通过分配工作更快地获得了这些结果。

## 链接后续步骤

[Ray Tune](https://anyscale.com/library/ray-tune) 可以轻松地在本地或云中的多台计算机上的多个节点上自动化和分发超参数调整。

正如我们所看到的，使用 Ray Tune 的 TuneSearchCV 替换 scikit-learn 的 RandomizedSearchCV，在 Ray 集群上运行使我们能够轻松地将超参数调整过程分布在多个节点上。这最多可以将调整所需的时间减少 N 倍（其中 N 是 Ray 集群中的节点数量），因为分布式计算总是有一些开销。

如果您想快速调整模型的超参数，请考虑尝试 Ray 和 [Ray Tune](https://docs.ray.io/en/latest/tune/index.html) 来改进您自己的模型 - 如果您想使用 Ray，但不想管理或扩展自己的集群，请[注册 Anyscale](https://www.anyscale.com/beta)。

#### 目录

- [将超参数调整移植到 Ray Tune ](https://www.anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune#porting-hyperparameter-tuning-to-ray-tune-)
- [分布式超参数调优处理](https://www.anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune#distributing-hyperparameter-tuning-processing)
- [后续步骤](https://www.anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune#next-steps)

####分享

####标签

射线调谐

#### 注册产品更新

####推荐内容

![宣布 Ray 在 Google TPU 上支持 PyTorch](https://images.ctfassets.net/xjan103pcp94/5odqs3bDXHHrUGye7EReO6/12a5fb11fc7d119b1ce905d420821160/ExternalRayTorchTPUblog.png?w=140)

#### 宣布 Ray 在 Google TPU 上支持 PyTorch

![使用 KubeRay 在 Kubernetes 上大规模运行 Ray](https://images.ctfassets.net/xjan103pcp94/6rF9ECqCFk5OjE7RftoynJ/e003a1df2ce07a3177dbdd4d1fe76473/Running_Ray_at_scale_on_Kubernetes_with_KubeRay.png?w=140)

#### 使用 KubeRay 在 Kubernetes 上大规模运行 Ray

![机器人决策科学](https://images.ctfassets.net/xjan103pcp94/AH4SiTdLoUM2EzlqZvNq5/20c1da7d646dabf59144a0aa7a0af0d8/Science_of_Robot_Decisions.png?w=140)

#### 使用 Ray 在任意尺度上扩展机器人决策科学

## 立即探索 Anyscale

使用专为生产 AI 构建的多云平台，在 Ray 上构建、运行和扩展任何 AI 工作负载。

[免费开始](https://authkit.anyscale.com/?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)[与专家交谈](https://www.anyscale.com/book/demo?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)
