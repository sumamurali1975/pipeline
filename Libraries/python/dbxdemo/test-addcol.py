# test-addcol.py
import pytest
import pyspark.sql.functions as F
from pyspark.sql import *


class TestAppendCol(object):

  def with_status(self, df):
      return df.withColumn("status", F.lit("checked"))

  def get_spark(self):
     spark = SparkSession.builder.getOrCreate()
     return spark

  def test_with_status(self):
    source_data = [
        ("paula", "white", "paula.white@example.com"),
        ("john", "baer", "john.baer@example.com")
    ]
    source_df = self.get_spark().createDataFrame(
        source_data,
        ["first_name", "last_name", "email"]
    )

    actual_df = self.with_status(source_df)

    expected_data = [
        ("paula", "white", "paula.white@example.com", "checked"),
        ("john", "baer", "john.baer@example.com", "checked")
    ]
    expected_df = self.get_spark().createDataFrame(
        expected_data,
        ["first_name", "last_name", "email", "status"]
    )

    assert(expected_df.collect() == actual_df.collect())