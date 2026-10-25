---
vendor: anyscale
title: How to distribute hyperparameter tuning using Ray Tune
original_title: How to distribute hyperparameter tuning using Ray Tune
url: https://anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune
date: 2022-02-15
lang: en
captured: 2026-10-25
extractor: readability-v1
status: ok
body_sha: 5f229b83ec93
---

[Home](https://www.anyscale.com/)[Blog](https://www.anyscale.com/blog)Blog Detail

# How to distribute hyperparameter tuning using Ray Tune

By [Juan Navas](https://www.anyscale.com/blog?author=juan-navas) and [Richard Liaw](https://www.anyscale.com/blog?author=richard-liaw) | February 15, 2022

💡 *This blog post is part 3 in our series on hyperparameter tuning. If you're just getting started, check out part 1, *[*What is hyperparameter tuning?*](https://www.anyscale.com/blog/what-is-hyperparameter-tuning)*. In part 2, *[*How to tune hyperparameters on XGBoost*](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost)*, we explore a practical hands-on example.*

In the first article of our three-part series, we learned how [tuning hyperparameters](https://www.anyscale.com/blog/what-is-hyperparameter-tuning) helps find the optimal settings for the best results from our machine learning model. Then, in the second article, we learned [how to perform hyperparameter tuning on XGBoost](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost), and discovered that our tuned model makes more accurate predictions than our untuned model.

Depending on the search space, it can take a long time to execute search algorithms for hyperparameter tuning, from hours to days. When we ran the random search function in the previous article, we saw how costly it is in computing resources and time.

To tune hyperparameters quicker—without compromising quality—we need to employ distributed computing, which enables us to try different hyperparameters combinations in parallel.

In this final article of the series, we’ll demonstrate how to use the [Ray Tune](https://anyscale.com/library/ray-tune) library to distribute the hyperparameter tuning task among several computers. We’ll demonstrate using the distributed machine learning toolkit to tune hyperparameters on multiple local CPUs or in the cloud. We’ll continue to optimize our digit identification model, but we’ll do it quicker by distributing the task.

## LinkPorting hyperparameter tuning to Ray Tune

[The Ray project](https://www.anyscale.com/ray-open-source) has developed [tune-sklearn](https://github.com/ray-project/tune-sklearn) to serve as a drop-in replacement for scikit-learn’s grid search and random search hyperparameter tuning models, GridSearchCV and RandomizedSearchCV, respectively. It also supports additional search models, like Bayesian search, tree-structured Parzen estimators, and others. It’s just a matter of setting the input parameter **search_optimization** to **bayesian** or **bohb** for Bayesian Optimization, or **hyperopt** for tree-structured Parzen estimators.

Tune-sklearn also seamlessly integrates with Ray Tune for distributed hyperparameter tuning across several machines — locally or in the cloud — without the need to change our code.

Here, we’ll adapt the code we wrote in the [previous article](https://www.anyscale.com/blog/how-to-tune-hyperparameters-on-xgboost) to replace the `RandomizedSearchCV()` function with `tune-sklearn`.

First, we install tune-sklearn. In our console command line, we type one of the following:

`$ pip install tune-sklearn "ray[tune]"`

Or:

`$ pip install -U git+https://github.com/ray-project/tune-sklearn.git && pip install 'ray[tune]'`

Then, we update the code, replacing `RandomizedSearchCV` with `TuneSearchCV`. The code’s final version is as follows, with in-line comments explaining the modifications:

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

Next, we save the code above in a .py file. For example, **mnist_tune_search.py**. Then we run this file from the console CLI:

`$ python mnist_tune_search.py `

Ray Tune now starts several processes (workers) in parallel to perform the evaluation iterations, depending on our computer’s architecture (number of CPUs and number of cores per CPU).

With `verbose` set to 2, we can expect output similar to the text below:

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

The process took over 12 minutes, and it has found the best hyperparameter combination that increases the accuracy to 84.8 percent (from 82.6 percent with the default hyperparameter values, as seen in the previous article).

## LinkDistributing hyperparameter tuning processing

Next, we’ll distribute the hyperparameter tuning load among several computers. We’ll distribute our tuning using [Ray](https://www.ray.io/). We’ll build a Ray cluster comprising a head node and a set of worker nodes. We need to start the head node first. The workers then connect to it.

![blog-distrubuted-hyperparameter-tuning-processing](https://images.ctfassets.net/xjan103pcp94/4BkQcFkzVe4ZYUrov8NzZ3/ceeea98bfc3feca6b43ef52168defdff/blog-distrubuted-hyperparameter-tuning-processing.png)

blog-distrubuted-hyperparameter-tuning-processing

First, we need to install the Ray module. In our console CLI, we enter the following command:

`$ pip install ray`

Note that it’s vital to ensure the environment is precisely the same on all nodes participating in the cluster for this exercise. Pay close attention to the versions of Ray and XGBoost. We’ve tested the code in this tutorial on the following versions:

```
1$ pip show ray 
2Name: ray
3Version: 1.7.0
4
5$ pip show xgboost
6Name: xgboost
7Version: 1.2.0
```

Next, we make the following adaptations to our previous function:

- Copy the data files to the same directory for all nodes in the Ray cluster. Use an absolute path such as `/var/data`.
- Import Ray library.
- Initialize Ray to connect to the local node, `ray.init(address='auto')`.
- Decorate the function `tune_search_tuning()` as a Ray task with @ray.remote before the function declaration.
- Update the data files’ full paths to correspond with where they have been copied. For example: `/var/data/mnist_train_final.csv`
- Add the creation and handling of the workers to the main function.
- Move the time counter to the main function.

The new code is below, with changes commented in-line:

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

Save the code above in a file, such as **mnist_ray_tune_distributed.py**.

Before running the code above, you need to start a Ray cluster. Extensive documentation is available in the [Ray Cluster Overview](https://docs.ray.io/en/latest/cluster/index.html) docs. This documentation will show you how to start the Ray cluster on any cloud provider. It includes detailed information about popular cloud providers like AWS, GCP, and Azure. However, you can also run a ray cluster locally on-premises by initiating the head node and the workers on different servers.

A simple way to set up a Ray cluster on-premises is by manually starting a head node and attaching workers to it from the command line:

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

Now that the head node is running, we can connect the worker nodes using the Redis password provided by the `ray start --head` command. On the rest of the nodes in the Ray cluster, enter the following in the command line, replacing the IP address with that of the actual head node in your environment:

`$ ray start --address='192.168.0.196:6379' --redis-password='5241590000000000'`

Once the Ray cluster is running, we just need to run the Python script on one of the nodes. In the current exercise, we’ve set up a Ray cluster of two nodes. At one of the nodes, we enter the following in the command line:

`$ python mnist_ray_tune_distributed.py`

We expect an output like this:

```
1INFO worker.py:827 -- Connecting to existing Ray cluster at address: 192.168.0.196:6379
2.
3. 
4. 
5Accuracy:  0.82
6Total elapsed time:  315.5932471752167
7Best params from main function:  {'max_depth': 3, 'learning_rate': 0.1, 'subsample': 0.9, 'colsample_bytree': 0.6, 'colsample_bylevel': 0.9, 'n_estimators': 1000, 'num_class': 10}
```

The test ran in 315 seconds (approximately 5 minutes). That’s less than half the time of the previous test, where the Python script ran on a single node and took 741 seconds. Also, the new test’s accuracy is 82.0 percent for the best hyperparameter combination, similar to the results we obtained previously with the scikit-learn RandomizedSearchCV function (85.8 percent).

Distributing our hyperparameter tuning across a cluster ran much faster than on a single computer. Although our results were virtually identical to scikit-learn, we got those results faster by distributing the work.

## LinkNext Steps

[Ray Tune](https://anyscale.com/library/ray-tune) makes it easy to automate and distribute hyperparameter tuning across multiple nodes on multiple machines either locally or in the cloud.

As we saw, using Ray Tune’s TuneSearchCV to replace scikit-learn’s RandomizedSearchCV, running on a Ray cluster allowed us to easily distribute the hyperparameter tuning process across multiple nodes. This can, at most, reduce the time needed to tune by a factor of N — where N is the number of nodes in your Ray cluster — since distributed computing always has some overhead.

If you want to tune your model's hyperparameters quickly, consider trying out Ray and [Ray Tune](https://docs.ray.io/en/latest/tune/index.html) to improve your own models — and [sign up for Anyscale](https://www.anyscale.com/beta) if you’d like to use Ray, but don't want to manage or scale your own cluster.

#### Table of contents

- [Porting hyperparameter tuning to Ray Tune ](https://www.anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune#porting-hyperparameter-tuning-to-ray-tune-)
- [Distributing hyperparameter tuning processing](https://www.anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune#distributing-hyperparameter-tuning-processing)
- [Next Steps](https://www.anyscale.com/blog/how-to-distribute-hyperparameter-tuning-using-ray-tune#next-steps)

#### Sharing

#### Tags

Ray Tune

#### Sign up for product updates

#### Recommended content

![Announcing Ray support for PyTorch on Google TPUs](https://images.ctfassets.net/xjan103pcp94/5odqs3bDXHHrUGye7EReO6/12a5fb11fc7d119b1ce905d420821160/ExternalRayTorchTPUblog.png?w=140)

#### Announcing Ray support for PyTorch on Google TPUs


![Running Ray at scale on Kubernetes with KubeRay](https://images.ctfassets.net/xjan103pcp94/6rF9ECqCFk5OjE7RftoynJ/e003a1df2ce07a3177dbdd4d1fe76473/Running_Ray_at_scale_on_Kubernetes_with_KubeRay.png?w=140)

#### Running Ray at scale on Kubernetes with KubeRay


![Science of Robot Decisions](https://images.ctfassets.net/xjan103pcp94/AH4SiTdLoUM2EzlqZvNq5/20c1da7d646dabf59144a0aa7a0af0d8/Science_of_Robot_Decisions.png?w=140)

#### Scaling the Science of Robot Decisions with Ray on Anyscale


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

[Start for Free](https://authkit.anyscale.com/?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)[Talk to an expert](https://www.anyscale.com/book/demo?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)
