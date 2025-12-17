import pandas

df = pandas.read_csv("datasets/xacml/xacBench-datasets/xacml-policies/xacml3_3.csv")
print(df.describe())
