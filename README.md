# Mean Reversion Trading Bot for Bitget

A trading bot designed to run on the [Bitget](https://www.bitget.com/) platform using a z-score based mean reversion trading strategy. This bot continuously monitors market prices, calculates the z-score to determine deviations from the mean, and executes trades based on configurable entry and exit thresholds.


## Features

- **Automated Trading:** Executes trades on Bitget based on a statistical mean reversion strategy.
- **Z-Score Calculation:** Uses historical price data to compute the z-score for identifying overextended price moves.
- **Customizable Parameters:** Configure trading pair, trade size, z-score thresholds, and other parameters.
- **Real-Time Data Monitoring:** Continuously retrieves and analyzes market data.
- **Logging & Error Handling:** Keeps detailed logs of trading activity and errors for debugging and performance tracking.
