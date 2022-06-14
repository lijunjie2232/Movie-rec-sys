import pandas as pd
import numpy as np
# # from tqdm.notebook import tqdm
# # import time
# import random
#
# #
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl


#
#
# def reduce_mem(df):
#     starttime = time.time()
#     numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
#     start_mem = df.memory_usage().sum() / 1024 ** 2
#     for col in df.columns:
#         col_type = df[col].dtypes
#         if col_type in numerics:
#             c_min = df[col].min()
#             c_max = df[col].max()
#             if pd.isnull(c_min) or pd.isnull(c_max):
#                 continue
#             if str(col_type)[:3] == 'int':
#                 if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
#                     df[col] = df[col].astype(np.int8)
#                 elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
#                     df[col] = df[col].astype(np.int16)
#                 elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
#                     df[col] = df[col].astype(np.int32)
#                 elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
#                     df[col] = df[col].astype(np.int64)
#             else:
#                 if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
#                     df[col] = df[col].astype(np.float16)
#                 elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
#                     df[col] = df[col].astype(np.float32)
#                 else:
#                     df[col] = df[col].astype(np.float64)
#     end_mem = df.memory_usage().sum() / 1024 ** 2
#     print('-- Mem. usage decreased to {:5.2f} Mb ({:.1f}% reduction),time spend:{:2.2f} min'.format(end_mem, 100 * (
#             start_mem - end_mem) / start_mem, (time.time() - starttime) / 60))
#     return df
#
#
# def get_click_random_sample(num):
#     r_num = random.sample(range(0, 17), num)
#     print(r_num)
#     samples = []
#     for i in r_num:
#         samples.append(pd.read_csv('./app/comm/output/predict_user_item_sample/predict_usage_data_random_sample_%s.csv' % i))
#     return samples
#
#
# # print(get_click_random_sample(7))
#
# class MovieLensTrainDataset(Dataset):
#     """MovieLens PyTorch Dataset for Training
#
#     Args:
#         ratings (pd.DataFrame): Dataframe containing the movie ratings
#         all_movieIds (list): List containing all movieIds
#
#     """
#
#     def __init__(self, ratings, all_movieIds):
#         self.users, self.items, self.labels = self.get_dataset(ratings, all_movieIds)
#
#     def __len__(self):
#         return len(self.users)
#
#     def __getitem__(self, idx):
#         return self.users[idx], self.items[idx], self.labels[idx]
#
#     def get_dataset(self, ratings, all_movieIds):
#         users, items, labels = [], [], []
#         user_item_set = set(zip(ratings['userId'], ratings['movieId']))
#
#         num_negatives = 4
#         for u, i in user_item_set:
#             users.append(u)
#             items.append(i)
#             labels.append(1)
#             for _ in range(num_negatives):
#                 negative_item = np.random.choice(all_movieIds)
#                 while (u, negative_item) in user_item_set:
#                     negative_item = np.random.choice(all_movieIds)
#                 users.append(u)
#                 items.append(negative_item)
#                 labels.append(0)
#
#         return torch.tensor(users), torch.tensor(items), torch.tensor(labels)


#
#

class MovieLensTrainDataset(Dataset):
    """MovieLens PyTorch Dataset for Training

    Args:
        ratings (pd.DataFrame): Dataframe containing the movie ratings
        all_movieIds (list): List containing all movieIds

    """

    def __init__(self, ratings, all_movieIds):
        self.users, self.items, self.labels = self.get_dataset(ratings, all_movieIds)

    def __len__(self):
        return len(self.users)

    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.labels[idx]

    def get_dataset(self, ratings, all_movieIds):
        users, items, labels = [], [], []
        user_item_set = set(zip(ratings['userId'], ratings['movieId']))

        num_negatives = 4
        for u, i in user_item_set:
            users.append(u)
            items.append(i)
            labels.append(1)
            for _ in range(num_negatives):
                negative_item = np.random.choice(all_movieIds)
                while (u, negative_item) in user_item_set:
                    negative_item = np.random.choice(all_movieIds)
                users.append(u)
                items.append(negative_item)
                labels.append(0)

        return torch.tensor(users), torch.tensor(items), torch.tensor(labels)


class NCF(pl.LightningModule):
    """ Neural Collaborative Filtering (NCF)

        Args:
            num_users (int): Number of unique users
            num_items (int): Number of unique items
            ratings (pd.DataFrame): Dataframe containing the movie ratings for training
            all_movieIds (list): List containing all movieIds (train + test)
    """

    def __init__(self, num_users, num_items, ratings, all_movieIds):
        super().__init__()
        self.user_embedding = nn.Embedding(num_embeddings=num_users, embedding_dim=8)
        self.item_embedding = nn.Embedding(num_embeddings=num_items, embedding_dim=8)
        self.fc1 = nn.Linear(in_features=16, out_features=64)
        self.fc2 = nn.Linear(in_features=64, out_features=32)
        self.output = nn.Linear(in_features=32, out_features=1)
        self.ratings = ratings
        self.all_movieIds = all_movieIds

    def forward(self, user_input, item_input):
        # Pass through embedding layers
        user_embedded = self.user_embedding(user_input)
        item_embedded = self.item_embedding(item_input)

        # Concat the two embedding layers
        vector = torch.cat([user_embedded, item_embedded], dim=-1)

        # Pass through dense layer
        vector = nn.ReLU()(self.fc1(vector))
        vector = nn.ReLU()(self.fc2(vector))

        # Output layer
        pred = nn.Sigmoid()(self.output(vector))

        return pred

    def training_step(self, batch, batch_idx):
        user_input, item_input, labels = batch
        predicted_labels = self(user_input, item_input)
        loss = nn.BCELoss()(predicted_labels, labels.view(-1, 1).float())
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters())

    def train_dataloader(self):
        return DataLoader(MovieLensTrainDataset(self.ratings, self.all_movieIds),
                          batch_size=512, num_workers=0)
#
#
# def get_torch_model():
#     return torch.load('./app/comm//output/torch_model.pth')
#
#
