from collections.abc import MutableMapping
import pickle
from hashlib import md5
import pandas as pd

def TFConvertor(data, newtf):
    # refining data and fill missed values with nan to have a good resampling
    # find frequency of data (minimum freq)
    frequncies = (pd.Series(data.index[1:]) -
                  pd.Series(data.index[:-1])).value_counts()
    # generate time series in data period with its freq
    fine_indices = pd.period_range(
        data.index.min(), data.index.max(), freq=frequncies.index.min())
    fine_indices = fine_indices.to_timestamp()
    # refine indices (empty ones fill with nan)
    data = data.reindex(fine_indices)

    # resampling  // first,last,min,max,mean,sum,...  //T or M for min, H for hour, D for day, M, Y,...
    Open = data.Open.resample(newtf).first()
    Open = Open.to_frame()
    Close = data.Close.resample(newtf).last()
    Close = Close.to_frame()
    High = data.High.resample(newtf).max()
    High = High.to_frame()
    Low = data.Low.resample(newtf).min()
    Low = Low.to_frame()
    Volume = data.Volume.resample(newtf).sum()
    Volume = Volume.to_frame()

    newtfdata = Open
    newtfdata['High'] = High['High']
    newtfdata['Low'] = Low['Low']
    newtfdata['Close'] = Close['Close']
    newtfdata['Volume'] = Volume['Volume']

    # remove nan vals
    newtfdata = newtfdata.dropna()

    return newtfdata

def CreateTimeFrames(data, timeframes):
    new_data = {}
    for t in timeframes:
        new_data[t] = TFConvertor(data, t)
    return new_data


class DuplicateCounter(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.storage = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.storage[key]

    def __setitem__(self, key, value):
        hash_key = self.__keytransform__(key)
        if hash_key in self.storage:
            self.storage[hash_key] = self.storage[hash_key] + [value]
        else:
            self.storage[hash_key] = [value]

    def __delitem__(self, key):
        del self.storage[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.storage)

    def __len__(self):
        return len(self.storage)

    def __keytransform__(self, key):
        return str(key)
        # return md5(pickle.dumps(key)).hexdigest()

    def count(self):
        result = []
        for _, v in self.storage.items():
            length = len(v)
            if length <= 1:
                result += v
                continue
            for ind in v:
                ind.duplicate_number = length
            result += v

        return result
