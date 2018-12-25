import pandas as pd
import xgboost as xgb
from sklearn import metrics
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import accuracy_score  # 准确率
from matplotlib import pyplot

# path to where the data lies
tests = pd.read_csv(r'.\test_data4.csv')
trains = pd.read_csv(r'.\train_data4.csv')
# print(tests.dtypes)

# ENTER_DATE      MOD_DATE   STATUS_DATE     object
tests['ENTER_DATE'] = pd.to_datetime(pd.Series(tests['ENTER_DATE']))
tests['MOD_DATE'] = pd.to_datetime(pd.Series(tests['MOD_DATE']))
tests['STATUS_DATE'] = pd.to_datetime(pd.Series(tests['STATUS_DATE']))

tests['ENTER_DATE_Year'] = tests['ENTER_DATE'].apply(lambda x: x.year)
tests['ENTER_DATE_Month'] = tests['ENTER_DATE'].apply(lambda x: x.month)
tests['ENTER_DATE_weekday'] = tests['ENTER_DATE'].dt.dayofweek
tests['ENTER_DATE_time'] = tests['ENTER_DATE'].dt.time

tests['MOD_DATE_Year'] = tests['MOD_DATE'].apply(lambda x: x.year)
tests['MOD_DATE_Month'] = tests['MOD_DATE'].apply(lambda x: x.month)
tests['MOD_DATE_weekday'] = tests['MOD_DATE'].dt.dayofweek
tests['MOD_DATE_time'] = tests['MOD_DATE'].dt.time

tests['STATUS_DATE_Year'] = tests['STATUS_DATE'].apply(lambda x: x.year)
tests['STATUS_DATE_Month'] = tests['STATUS_DATE'].apply(lambda x: x.month)
tests['STATUS_DATE_weekday'] = tests['STATUS_DATE'].dt.dayofweek
tests['STATUS_DATE_time'] = tests['STATUS_DATE'].dt.time
# 删除
tests = tests.drop('MOD_DATE', axis=1)
tests = tests.drop('ENTER_DATE', axis=1)
tests = tests.drop('STATUS_DATE', axis=1)

# ENTER_DATE      MOD_DATE   STATUS_DATE     object
trains['ENTER_DATE'] = pd.to_datetime(pd.Series(trains['ENTER_DATE']))
trains['MOD_DATE'] = pd.to_datetime(pd.Series(trains['MOD_DATE']))
trains['STATUS_DATE'] = pd.to_datetime(pd.Series(trains['STATUS_DATE']))

trains['ENTER_DATE_Year'] = trains['ENTER_DATE'].apply(lambda x: x.year)
trains['ENTER_DATE_Month'] = trains['ENTER_DATE'].apply(lambda x: x.month)
trains['ENTER_DATE_weekday'] = trains['ENTER_DATE'].dt.dayofweek
trains['ENTER_DATE_time'] = trains['ENTER_DATE'].dt.time

trains['MOD_DATE_Year'] = trains['MOD_DATE'].apply(lambda x: x.year)
trains['MOD_DATE_Month'] = trains['MOD_DATE'].apply(lambda x: x.month)
trains['MOD_DATE_weekday'] = trains['MOD_DATE'].dt.dayofweek
trains['MOD_DATE_time'] = trains['MOD_DATE'].dt.time

trains['STATUS_DATE_Year'] = trains['STATUS_DATE'].apply(lambda x: x.year)
trains['STATUS_DATE_Month'] = trains['STATUS_DATE'].apply(lambda x: x.month)
trains['STATUS_DATE_weekday'] = trains['STATUS_DATE'].dt.dayofweek
trains['STATUS_DATE_time'] = trains['STATUS_DATE'].dt.time

trains = trains.drop('MOD_DATE', axis=1)
trains = trains.drop('ENTER_DATE', axis=1)
trains = trains.drop('STATUS_DATE', axis=1)

# print(tests.dtypes)
# print(tests)
# print(tests.info())

feature_columns_to_use = [  # "CUST_ID",
    # "CUST_NUMBER",
    "PWD_FLAG",
    "PWD_STAT",
    "ADDRESS_ID",
    "CUST_PROP",
    "CUST_TYPE_ID",
    "CUST_CLASS_DL",
    "CUST_CLASS_ZL",
    "CUST_CLASS_XL",
    "SERV_LEV",
    "SECRECY_LEV",
    "CONSUME_GRADE",
    "CREDIT_DEG",
    "CUST_SOURCE",
    # "STATE",
    "VIP_CODE",
    "FOREIGN_NAME",
    "CUST_KIND",
    "COMMON_REGION_ID",
    "CUST_TYPE",
    "CUST_SUB_TYPE",
    "CUST_AREA_GRADE",
    "INDUSTRY_CD",
    "RELA_NAME",
    "REMARK_TYPE",
    # "DURATION",
    "SEX",
    "AGE",
    "RMK_11808",
    "RMK_BND",
    "RMK_3G",
    "RMK_CAMPUS",
    "RMK_LINE",
    "RMK_VIP_CARD",
    "RMK_PKG",
    "RMK_FRQ_CUST",
    "RMK_SALES",
    "RMK_CO_GOV",
    "RMK_FAMILY",
    "RMK_XLT",
    "ENTER_DATE_Year",
    "ENTER_DATE_Month",
    "ENTER_DATE_weekday",
    "MOD_DATE_Year",
    "MOD_DATE_Month",
    "MOD_DATE_weekday",
    "STATUS_DATE_Year",
    "STATUS_DATE_Month",
    "STATUS_DATE_weekday"]

train_for_matrix = trains[feature_columns_to_use]
test_for_matrix = tests[feature_columns_to_use]
train_X = train_for_matrix.as_matrix()
print(trains.info())
# label
train_Y = trains["STATUS_CD"]
print(trains.info())
test_X = test_for_matrix.as_matrix()
# print(test_Y)


gbm = xgb.XGBClassifier(silent=0, max_depth=5,
                        n_estimators=100, learning_rate=0.1)
gbm.fit(train_X, train_Y)
predictions = gbm.predict(test_X, output_margin=True)
ss = gbm.predict_proba(test_X)
print("#####")
print(type(ss))
submission = pd.DataFrame({'CUST_ID': tests['CUST_ID'],
                           'STATUS_CD': tests['STATUS_CD'],
                           'STATUS_PRED': predictions,
                           'prob0': ss[:, 0],
                           'prob1': ss[:, 1],
                           })

print(submission)

# 准确率
accuracy = accuracy_score(tests['STATUS_CD'], predictions)
print("accuarcy: %.2f%%" % (accuracy * 100.0))
print("precision_score:", metrics.precision_score(tests['STATUS_CD'], predictions))
print("recall_score:", metrics.recall_score(tests['STATUS_CD'], predictions))

xgb.plot_importance(gbm)
pyplot.show()
submission.to_csv("submission.csv", index=False)
