# SABRmodelOptionArbitrage
High Frequency Option Arbitrage Based on SABR model  
reference: https://github.com/yuba316/SABR_Volatility_Arbitrage.git

## Requirement
python >= 3.6.13  
numpy >= 1.19.5  
pandas >= 0.25.3  
scipy >= 1.5.3  
matplotlib >= 3.3.4  


## Code Explanation

(1) dataloader.py  
 - Collect option trading data from raw data.
 - Raw data is restricted and no provided.

(2) calcualtor.py   
 - Calculate IV and other Greek based on BSM model or SABR model.

(3) calibrator.py   
 - Calibrate SABR parameters and simulate IV based on SABR.

(4) stragety.py   
 - Get signal and position based on difference between market BSM IV and SABR IV.
 - Back test by given position.

main.py -- SABR Calibrating and Stragety Testing  

## Usage
- Run **dataloader.py** for data collecting(unnecessary if no raw data)   
- Run **main.py** for Calibrating and Testing

## Output
position.csv : SARB IV and position for option contracts.   
portfolio.csv : portfolio return.  
other metrics: statistic metrics for portfolio return.  
