#### **Please have the fidelity mobile app installed
## Installation
### Docker (currently not working, use python)
1. Clone repository into folder: `git clone https://github.com/TheRealFanjin/fidelity-api.git`
2. `cd fidelity-api`
3. Enter your Fidelity username and password along with your Discord Bot token (requires message intent) into `prod.env` and rename the file to just `.env`
4. Build Docker image with `docker build fid .`
5. Run Docker image with `docker run fid`

### Python
1. This project is made in Python 3.10. It may work on other versions but is not guaranteed
2. Clone repository into folder: `git clone https://github.com/TheRealFanjin/fidelity-api.git`
3. `cd fidelity-api`
4. Enter your Fidelity username and password along with your Discord Bot token (requires message intent) into `prod.env` and rename the file to just `.env`
5. `pip install -r requirements.txt`
6. Run main.py `python main.py`

## Usage
`.buy {stock} {accounts (leave empty for all)}`

`.sell {stock} {accounts {leave empty for all)}`

`.balances {accounts (leave empty for all)}`