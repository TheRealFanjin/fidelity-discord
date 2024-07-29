## Installation
1. Clone repository into folder: `git clone https://github.com/TheRealFanjin/fidelity-api.git`
2. `cd fidelity-api`
3. Enter your Fidelity username and password along with your Discord Bot token (requires message intent) into `prod.env` and rename the file to just `.env`
4. Build Docker image with `docker build fid .`
5. Run Docker image with `docker run fid`