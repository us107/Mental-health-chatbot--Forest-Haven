from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, round

# Initialize Spark
spark = SparkSession.builder \
    .appName("MentalHealthStats") \
    .master("local[2]") \
    .getOrCreate()

# Load dataset with explicit schema to avoid type inference issues
df = spark.read.csv("dataset.csv", header=True, inferSchema=True)

# Total count per country
total_by_country = df.groupBy("Country").agg(count("*").alias("total"))

# Stress stats (Growing_Stress = Yes)
stress_by_country = df.filter(col("Growing_Stress") == "Yes") \
    .groupBy("Country").agg(count("*").alias("stress_count"))

# Mood swings stats (Mood_Swings = High or Medium)
mood_by_country = df.filter(col("Mood_Swings").isin("High", "Medium")) \
    .groupBy("Country").agg(count("*").alias("mood_count"))

# Join and calculate percentages
stats = total_by_country \
    .join(stress_by_country, "Country", "left") \
    .join(mood_by_country, "Country", "left") \
    .fillna(0, subset=["stress_count", "mood_count"]) \
    .withColumn("stress_percent", round((col("stress_count") / col("total")) * 100, 2)) \
    .withColumn("mood_percent", round((col("mood_count") / col("total")) * 100, 2))

# Show results
stats.show()

# Save for chatbot
stats_df = stats.toPandas()
stats_df.to_csv("mental_health_stats.csv", index=False)

spark.stop()