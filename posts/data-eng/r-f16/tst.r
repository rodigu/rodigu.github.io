library(arrow)

df <- read_parquet("./posts/data-eng/r-f16/data.parquet")
print(df)

print('arrow version')
print(packageVersion('arrow'))
print('session info')
print(sessionInfo())
