# Sample Datasets for Mantua.AI

These are synthetic/example datasets.

Intended for testing/demo only (not production).

## How to Load and Use Them for Development

These sample CSV files are provided to help you test and develop features in Mantua.AI without relying on live market data. Each CSV includes the following columns:

* `timestamp_ms`: Unix timestamp in milliseconds
* `price`: Asset price at that timestamp
* `realised_volatility`: A placeholder for calculated volatility (currently `NaN`)

To use these datasets:

1. **Load the CSV using a data library**. For example, with Python and pandas:

   ```python
   import pandas as pd

   # Load a dataset
   df = pd.read_csv('datasets/samples/cbbtc_price_vol_sample.csv')

   # Convert timestamp to datetime (optional)
   df['timestamp'] = pd.to_datetime(df['timestamp_ms'], unit='ms')

   # Perform analysis or calculations...
   ```

2. **Perform your data processing**. You can compute metrics such as realized volatility by using window functions or other statistical methods on the `price` column.

3. **Integrate with Mantua.AI components**. Use these sample datasets to simulate API responses, test data ingestion pipelines, or develop visualization components without needing real-time data sources.

Remember: these files are for development and demonstration purposes only. They should not be used in production.
