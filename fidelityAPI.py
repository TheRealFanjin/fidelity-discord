import time
import re
import undetected_chromedriver as uc
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class fidelity:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __init_driver(self):
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options)
        return driver

    async def __login(self, ctx, driver):
        actions = ActionChains(driver)
        driver.get('https://digital.fidelity.com/ftgw/digital/portfolio/positions')
        time.sleep(3)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#dom-username-input'))).send_keys(self.username)
        time.sleep(2)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#dom-pswd-input'))).send_keys(
            self.password)
        time.sleep(4)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#dom-login-button'))).click()
        time.sleep(5)
        try:
            actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="dom-widget"]/div/div['
                                                                  '2]/pvd-field-group/s-root/div/div/s-slot/s'
                                                                  '-assigned-wrapper/pvd-form/s-root/div/form/s-slot'
                                                                  '/s-assigned-wrapper/div['
                                                                  '1]/div/div/pvd-field-group/s-root/div/div/s-slot/s'
                                                                  '-assigned-wrapper/pvd-checkbox/s-root/div/label')).click().perform()
            driver.find_element(By.CSS_SELECTOR, '//*[@id="dom-push-primary-button"]').click()
            while True:
                await ctx.send('Please approve login on mobile device. Retrying in 5 seconds...')
                time.sleep(5)
                try:
                    driver.find_element(By.XPATH, '//*[@id="accountDetails"]/div/div[1]/div[1]/h2/span[2]')
                    await ctx.send('Login approved')
                except NoSuchElementException:
                    continue
        except NoSuchElementException:
            pass

    def __enter_stock_details(self, driver, buy, stock):
        actions = ActionChains(driver)
        driver.find_element(By.XPATH, '//*[@id="eq-ticket-dest-symbol"]').send_keys(stock)
        time.sleep(3)
        try:
            actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="0"]/span[1]')).click().perform()
        except NoSuchElementException:
            return False
        time.sleep(3)
        if buy:
            actions.move_to_element(
                driver.find_element(By.XPATH, '//*[@id="action-buy"]/s-root/div')).click().perform()
            actions.move_to_element(
                driver.find_element(By.XPATH, '//*[@id="market-no"]/s-root/div')).click().perform()
        else:
            actions.move_to_element(
                driver.find_element(By.XPATH, '//*[@id="action-sell"]/s-root/div')).click().perform()
            actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="market-yes"]/s-root/div')).click().perform()
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="eqt-shared-quantity"]').send_keys('1')
        time.sleep(1)
        return True

    def __error_popup_check(self, driver):
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="placeOrderBtn"]'))).click()
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="order-reveived-lable"]')))
            return True
        except TimeoutException:
            try:
                error_text = driver.find_element(By.XPATH,
                                                 f"/html/body/div[3]/ap122489-ett-component/div/pvd3-modal["
                                                 f"1]/s-root/div/div[2]/div/div[1]/s-slot/s-assigned-wrapper/h2").text
                driver.find_element(By.XPATH,
                                    '/html/body/div[3]/ap122489-ett-component/div/pvd3-modal[1]/s-root/div/div['
                                    '2]/div/button').click()
                return error_text

            except NoSuchElementException:
                return False

    async def check_balances(self, ctx):
        driver = self.__init_driver()
        await self.__login(ctx, driver)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="posweb-grid"]/div[2]/div[2]/div[2]/div[1]')))
        accounts = {}
        counter = 1
        while True:
            skip_counter = counter
            stop_skip = False
            while True:
                try:
                    if driver.find_element(By.XPATH,
                                           f'//*[@id="posweb-grid"]/div[2]/div[2]/div[2]/div[3]/div[1]/div[1]/div[{skip_counter}]/div/div/span/div/div[2]/div/p').text == 'Grand Total':
                        stop_skip = True
                        break
                    elif driver.find_element(By.XPATH,
                                             f'//*[@id="posweb-grid"]/div[2]/div[2]/div[2]/div[3]/div[1]/div[1]/div[{skip_counter}]/div/div/span/div/div[2]/div/p').text == 'Account Total':
                        skip = skip_counter - counter
                        break
                    else:
                        skip_counter += 1
                except NoSuchElementException:
                    skip_counter += 1
            if stop_skip:
                break
            try:
                accounts[driver.find_element(By.XPATH,
                                             f'//*[@id="posweb-grid"]/div[2]/div[2]/div[2]/div[3]/div[1]/div[1]/div[{counter}]/div/div/span/div/div[2]/h3/span[3]').text] = driver.find_element(
                    By.XPATH,
                    f'//*[@id="posweb-grid"]/div[2]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{counter + skip}]/div[4]/div/span').text
                counter += skip + 2
            except NoSuchElementException:
                break
        driver.quit()
        return accounts

    async def __bs_on_all_accounts(self, ctx, buy, stocks):
        driver = self.__init_driver()
        await self.__login(ctx, driver)
        driver.get('https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry')
        for stock in stocks:
            counter = 0
            price0 = 0
            first = True
            while True:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="dest-acct-dropdown"]'))).click()
                try:
                    account_number = re.search(r'Z\d{8}', driver.find_element(By.XPATH,
                                                                              f'//*[@id="account{counter}"]').text).group()
                    driver.find_element(By.XPATH, f'//*[@id="ett-acct-sel-list"]/ul/li[{counter + 1}]').click()
                except NoSuchElementException:
                    break

                if first:
                    response = self.__enter_stock_details(driver, buy, stock)
                    if not response:
                        await ctx.send(f'Error finding {stock} for account {account_number}')
                        continue

                if buy:
                    price1 = float(driver.find_element(By.XPATH, '//*[@id="eq-ticket__last-price"]/span[2]').text[1:])
                    if price1 > price0:
                        driver.find_element(By.XPATH, '//*[@id="eqt-ordsel-limit-price-field"]').send_keys(
                            round(price1 + 0.05, 2))
                        price0 = round(price1 + 0.05, 2)
                time.sleep(2)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="previewOrderBtn"]/s-root/button'))).click()
                time.sleep(3)

                # check for errors
                error_response = self.__error_popup_check(driver)
                if buy:
                    if error_response is True:
                        await ctx.send(f'Successfully placed order for account {account_number} for {stock}')
                    elif error_response is False:
                        await ctx.send(f'Unknown Error/Timeout purchasing stock {stock} for account {account_number}')
                        break
                    else:
                        await ctx.send(f"""Failed to purchase {stock} on account {account_number}: {error_response}""")
                else:
                    if error_response is True:
                        await ctx.send(f'Successfully placed order for account {account_number} for {stock}')
                    elif error_response is False:
                        await ctx.send(f'Unknown Error/Timeout selling stock {stock} for account {account_number}')
                        break
                    else:
                        await ctx.send(f"""Failed to sell {stock} on account {account_number}: {error_response}""")
                counter += 1
                first = False
        await ctx.send('Tasks completed')
        driver.quit()

    async def __bs_on_specified_accounts(self, ctx, buy, stocks, accounts):
        driver = self.__init_driver()
        actions = ActionChains(driver)
        await self.__login(ctx, driver)
        driver.get('https://digital.fidelity.com/ftgw/digital/trade-equity/index/orderEntry')
        for stock in stocks:
            price0 = 0
            first = True
            not_found = False
            for account in accounts:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="dest-acct-dropdown"]'))).click()
                time.sleep(1.5)
                counter = 0
                while True:
                    try:
                        account_number = re.search(r'Z\d{8}', driver.find_element(By.XPATH,
                                                                                  f'//*[@id="account{counter}"]').text).group()
                        if account_number == account:
                            driver.find_element(By.XPATH,
                                                f'//*[@id="ett-acct-sel-list"]/ul/li[{counter + 1}]').click()
                            break
                        counter += 1
                    except NoSuchElementException:
                        await ctx.send(f'{accounts[0]} not found')
                        not_found = True

                if not_found:
                    continue
                if first:
                    response = self.__enter_stock_details(driver, buy, stock)
                    if not response:
                        await ctx.send(f'Error finding {stock} for account {account_number}')
                        continue
                if buy:
                    price1 = float(driver.find_element(By.XPATH, '//*[@id="eq-ticket__last-price"]/span[2]').text[1:])
                    if price1 > price0:
                        driver.find_element(By.XPATH, '//*[@id="eqt-ordsel-limit-price-field"]').send_keys(
                            round(price1 + 0.05, 2))
                        price0 = round(price1 + 0.05, 2)
                time.sleep(2)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="previewOrderBtn"]/s-root/button'))).click()
                time.sleep(3)

                # check for errors
                error_response = self.__error_popup_check(driver)
                if buy:
                    if error_response is True:
                        await ctx.send(f'Successfully placed order for account {account_number} for {stock}')
                    elif error_response is False:
                        await ctx.send(f'Unknown Error/Timeout purchasing stock {stock} for account {account_number}')
                        break
                    else:
                        await ctx.send(f"""Failed to purchase {stock} on account {account_number}: {error_response}""")
                else:
                    if error_response is True:
                        await ctx.send(f'Successfully placed order for account {account_number} for {stock}')
                    elif error_response is False:
                        await ctx.send(f'Unknown Error/Timeout selling stock {stock} for account {account_number}')
                        break
                    else:
                        await ctx.send(f"""Failed to sell {stock} on account {account_number}: {error_response}""")
                first = False
        await ctx.send('Tasks completed')
        driver.quit()

    async def bs(self, ctx, buy, stocks, accounts=None):
        if accounts is None:
            await self.__bs_on_all_accounts(ctx, buy, stocks)
        else:
            await self.__bs_on_specified_accounts(ctx, buy, stocks, accounts)

