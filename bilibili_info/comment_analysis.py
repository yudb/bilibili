# -*- coding: utf-8 -*-
# @Time    : 2021/3/9 18:58
# @Author  : YuDongbo
# @Email   : jayyudb@126.com
# @File    : comment_analysis.py
# @Software: PyCharm

from bilibili_info import sql

import jieba
import pickle
import os
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans


def load_comments():
    """
    将文本分词
    :return:
    """
    filename = 'data/bilibili_comments.pkl'
    # if os.path.exists(filename):
    #     with open(filename, 'rb') as in_data:
    #         comments = pickle.load(in_data)
    #         return comments

    stop_words = [word.strip() for word in open('data/stop_words.txt', 'r', encoding='utf-8').readlines()]

    db_comments = sql.get_comment()
    data=DataFrame(db_comments)
    print("正在分词...")
    # 分词，去除停用词
    data['comment'] = data['comment'].apply(lambda x: " ".join([word for word in jieba.cut(x) if word not in stop_words]))

    comments = []
    for comment in data['comment']:
        comments.append(comment)


    with open(filename, 'wb') as out_data:
        pickle.dump(comments, out_data, pickle.HIGHEST_PROTOCOL)

    return comments


def transform(comments, n_features=1000):
    """
    提取tf-idf特征
    :param comments:
    :param n_features:
    :return:
    """
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=n_features, min_df=2, use_idf=True)
    X = vectorizer.fit_transform(comments)
    return X, vectorizer


def train(X, vectorizer, true_k=10, mini_batch=False, show_label=False):
    """
    训练 k-means
    :param X:
    :param vectorizer:
    :param true_k:
    :param mini_batch:
    :param show_label:
    :return:
    """
    if mini_batch:
        k_means = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                                  init_size=1000, batch_size=1000, verbose=False)
    else:
        k_means = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=1,
                         verbose=False)
    k_means.fit(X)
    if show_label:  # 显示标签
        print("Top terms per cluster:")
        order_centroids = k_means.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        # print(vectorizer.get_stop_words())
        for i in range(true_k):
            print("Cluster %d" % i, end='')
            for ind in order_centroids[i, :10]:
                print(' %s' % terms[ind], end='')
            print()
    result = list(k_means.predict(X))
    print('Cluster distribution:')
    print(dict([(i, result.count(i)) for i in result]))
    return -k_means.score(X)


def plot_params():
    """
    测试选择最优参数
    :return:
    """
    comments = load_comments()
    print("%d docments" % len(comments))
    X, vectorizer = transform(comments, n_features=500)
    true_ks = []
    scores = []
    for i in range(3, 20, 1):
        score = train(X, vectorizer, true_k=i) / len(comments)
        print(i, score)
        true_ks.append(i)
        scores.append(score)
    plt.figure(figsize=(8, 4))
    plt.plot(true_ks, scores, label="error", color="red", linewidth=1)
    plt.xlabel("n_features")
    plt.ylabel("error")
    plt.legend()
    plt.show()


# plot_params()
def out():
    """
    在最优参数下输出聚类效果
    :return:
    """

    comments = load_comments()
    X, vectorizer = transform(comments, n_features=30)
    score = train(X, vectorizer, true_k=7, show_label=True) / len(comments)
    print(score)


if __name__ == "__main__":
    # plot_params()
    out()