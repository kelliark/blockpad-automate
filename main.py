import requests
import time
import random
import json
from datetime import datetime, timedelta, timezone
from colorama import init, Fore, Style
import sys
import threading
from queue import Queue
import os

init(autoreset=True)

class BlockpadAutomation:
    def __init__(self, bearer_token, proxy=None):
        self.base_url = "https://api3.blockpad.fun/api"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json',
            'Origin': 'https://testnet.blockpad.fun',
            'Referer': 'https://testnet.blockpad.fun/'
        }
        self.min_tice_balance = 10
        self.proxy = proxy
        self.session = self._create_session()
        
    def _create_session(self):
        session = requests.Session()
        if self.proxy:
            try:
                # Ensure proxy URL is properly formatted
                proxy_url = self.proxy
                if proxy_url.startswith('http://http://'):
                    proxy_url = 'http://' + proxy_url[13:]
                
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                session.proxies.update(proxies)
                
                # Extract domain for logging (remove credentials)
                domain = proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url
                self.log_with_time(f"Successfully configured proxy: {domain}", Fore.GREEN)
            except Exception as e:
                self.log_with_time(f"Error configuring proxy: {str(e)}", Fore.RED)
        return session
        
    def _make_request(self, method, url, **kwargs):
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                kwargs.setdefault('timeout', 30)  # Add a timeout to prevent hanging
                response = getattr(self.session, method)(url, **kwargs)
                return response
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    self.log_with_time(f"Request error (attempt {attempt + 1}/{max_retries}): {str(e)}", Fore.YELLOW)
                    time.sleep(retry_delay)
                else:
                    self.log_with_time(f"Request error: {str(e)}", Fore.RED)
        return None

    def log(self, message, color=Fore.WHITE):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}{message}{Style.RESET_ALL}")

    def log_with_time(self, message, color=Fore.WHITE):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.CYAN}[{timestamp}] {color}{message}{Style.RESET_ALL}")

    def get_user_info(self):
        response = self._make_request('get', f"{self.base_url}/auth/me", headers=self.headers)
        if response and response.status_code == 200:
            return response.json()['user']
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_with_time(f"Error getting user info: {error_msg}", Fore.RED)
            return None

    def display_user_stats(self):
        user = self.get_user_info()
        if user:
            self.log(f"\n{Fore.BLUE}[ User Statistics ]{Style.RESET_ALL}")
            self.log(f"{Fore.MAGENTA}Username     : {Fore.YELLOW}{user['username']}")
            self.log(f"{Fore.MAGENTA}tICE Balance : {Fore.GREEN}{user['tICEBalance']}")
            self.log(f"{Fore.MAGENTA}BPAD Balance : {Fore.GREEN}{user['BPADBalance']}")
            self.log(f"{Fore.MAGENTA}USDT Balance : {Fore.GREEN}{user['USDTBalance']}")
            self.log(f"{Fore.MAGENTA}XP Balance   : {Fore.GREEN}{user['xpBalance']}")

    def claim_faucet(self):
        self.log_with_time("Attempting to claim faucet...", Fore.YELLOW)
        response = self._make_request('post', f"{self.base_url}/faucet/claim", headers=self.headers)
        data = response.json()
        
        if 'error' in data:
            self.log_with_time(f"Faucet claim failed: {data['error']}", Fore.RED)
            return False
        else:
            self.log_with_time("Faucet claimed successfully!", Fore.GREEN)
            return True

    def execute_swap(self, from_token, to_token, amount):
        self.log_with_time(f"Executing swap: {amount} {from_token} → {to_token}", Fore.YELLOW)
        payload = {
            "fromToken": from_token,
            "toToken": to_token,
            "amount": amount
        }
        response = self._make_request('post', f"{self.base_url}/swap/execute", headers=self.headers, json=payload)
        if response and response.status_code == 200:
            self.log_with_time(f"Swap successful: {from_token} to {to_token}", Fore.GREEN)
            return True
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_with_time(f"Swap failed: {error_msg}", Fore.RED)
            return False

    def check_and_swap_to_tice(self):
        user = self.get_user_info()
        if float(user['tICEBalance']) < self.min_tice_balance:
            self.log_with_time("tICE balance is low. Converting other tokens to tICE...", Fore.YELLOW)
            
            bpad_balance = float(user['BPADBalance'])
            if bpad_balance > 0:
                self.log_with_time(f"Converting {bpad_balance} BPAD to tICE", Fore.YELLOW)
                self.execute_swap("BPAD", "tICE", bpad_balance)
            
            usdt_balance = float(user['USDTBalance'])
            if usdt_balance > 0:
                self.log_with_time(f"Converting {usdt_balance} USDT to tICE", Fore.YELLOW)
                self.execute_swap("USDT", "tICE", usdt_balance)
            
            return True
        return False

    def get_swap_amount(self, token, balance):
        if token in ["tICE", "BPAD"]:
            min_amount = 0.00001
            max_amount = min(10, float(balance))
            if max_amount <= min_amount:
                return 0
            return round(random.uniform(min_amount, max_amount), 6)
        else:  
            min_amount = 0.00001
            max_amount = min(100, float(balance))
            if max_amount <= min_amount:
                return 0
            return round(random.uniform(min_amount, max_amount), 6)

    def perform_task_swaps(self):
        self.log(f"\n{Fore.MAGENTA}[ Performing Swap Task ]{Style.RESET_ALL}")
        
        if self.check_and_swap_to_tice():
            self.log_with_time("Completed emergency tICE conversion", Fore.GREEN)
            return
            
        user = self.get_user_info()
        
        swap_pairs = [
            ("tICE", "BPAD"),
            ("tICE", "USDT"),
            ("BPAD", "tICE"),
            ("BPAD", "USDT"),
            ("USDT", "tICE"),
            ("USDT", "BPAD")
        ]
        
        for from_token, to_token in swap_pairs:
            balance_key = f"{from_token}Balance"
            balance = float(user[balance_key])
            
            if balance > 0:
                amount = self.get_swap_amount(from_token, balance)
                if amount > 0:
                    self.execute_swap(from_token, to_token, amount)
                    user = self.get_user_info()
                else:
                    self.log_with_time(f"Insufficient {from_token} balance for swap", Fore.YELLOW)

    def perform_liquidity_task(self):
        self.log(f"\n{Fore.MAGENTA}[ Performing Liquidity Task ]{Style.RESET_ALL}")
        
        self.check_and_swap_to_tice()
        
        user = self.get_user_info()
        if float(user['tICEBalance']) < 10 or float(user['BPADBalance']) < 1:
            self.log_with_time("Need to swap for required tokens first", Fore.YELLOW)
            if float(user['tICEBalance']) < 10:
                self.execute_swap("BPAD", "tICE", 1)
            if float(user['BPADBalance']) < 1:
                self.execute_swap("tICE", "BPAD", 10)
            user = self.get_user_info()
        
        if float(user['tICEBalance']) >= 10:
            self.log_with_time("Adding liquidity...", Fore.YELLOW)
            response = self._make_request('post', f"{self.base_url}/liquidity/add", 
                                   headers=self.headers, 
                                   json={"tICEAmount": 10})
            if response and response.status_code == 200:
                self.log_with_time("Liquidity added successfully!", Fore.GREEN)
                
                self.log_with_time("Removing liquidity...", Fore.YELLOW)
                remove_response = self._make_request('post', f"{self.base_url}/liquidity/remove", 
                                             headers=self.headers, 
                                             json={"tICEAmount": 10})
                if remove_response and remove_response.status_code == 200:
                    self.log_with_time("Liquidity removed successfully!", Fore.GREEN)
                    return True
        else:
            self.log_with_time("Insufficient balance for liquidity task", Fore.YELLOW)
        return False

    def perform_staking_task(self):
        self.log(f"\n{Fore.MAGENTA}[ Performing Staking Task ]{Style.RESET_ALL}")
        
        self.check_and_swap_to_tice()
        
        user = self.get_user_info()
        if float(user['tICEBalance']) < 1:
            self.log_with_time("Need to swap for tICE first", Fore.YELLOW)
            self.execute_swap("BPAD", "tICE", 1)
            user = self.get_user_info()
        
        if float(user['tICEBalance']) >= 1:
            self.log_with_time("Staking 1 tICE...", Fore.YELLOW)
            response = self._make_request('post', f"{self.base_url}/staking/stake", 
                                   headers=self.headers, 
                                   json={"token": "tICE", "amount": 1})
            if response and response.status_code == 200:
                self.log_with_time("Staking successful!", Fore.GREEN)
                
                self.log_with_time("Unstaking 1 tICE...", Fore.YELLOW)
                unstake_response = self._make_request('post', f"{self.base_url}/staking/unstake", 
                                              headers=self.headers, 
                                              json={"token": "tICE", "amount": 1})
                if unstake_response and unstake_response.status_code == 200:
                    self.log_with_time("Unstaking successful!", Fore.GREEN)
                    return True
        else:
            self.log_with_time("Insufficient balance for staking task", Fore.YELLOW)
        return False

    def perform_random_task(self):
        tasks = [
            self.perform_task_swaps,
            self.perform_liquidity_task,
            self.perform_staking_task
        ]
        task = random.choice(tasks)
        task()
        self.display_user_stats()

def load_tokens():
    if not os.path.exists('tokens.txt'):
        print(f"{Fore.RED}Error: tokens.txt file not found. Please create it with your bearer tokens.{Style.RESET_ALL}")
        sys.exit(1)
    
    with open('tokens.txt', 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_proxies():
    if not os.path.exists('proxy.txt'):
        return []
    
    with open('proxy.txt', 'r') as f:
        proxies = []
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Remove any protocol prefix if exists
            if line.startswith(('http://', 'https://', 'socks5://')):
                for prefix in ['http://', 'https://', 'socks5://']:
                    if line.startswith(prefix):
                        line = line[len(prefix):]
                        break

            # Split credentials and domain
            if '@' in line:
                credentials, domain = line.split('@', 1)
                # Create both HTTP and SOCKS5 versions
                proxies.extend([
                    f'http://{credentials}@{domain}',
                    f'socks5://{credentials}@{domain}'
                ])
            else:
                # If no credentials, just add domain with both protocols
                proxies.extend([
                    f'http://{line}',
                    f'socks5://{line}'
                ])
        
        return proxies

def run_account(token, proxy=None, proxy_list=None):
    max_retries = 3
    retry_count = 0
    current_proxy_index = 0

    while retry_count < max_retries:
        try:
            current_proxy = proxy
            if proxy_list and retry_count > 0:
                # Try a different proxy on retry
                current_proxy = proxy_list[current_proxy_index % len(proxy_list)]
                current_proxy_index += 1
            
            bot = BlockpadAutomation(token, current_proxy)
            bot.log_with_time(f"Attempting to connect with proxy: {current_proxy.split('@')[1] if '@' in current_proxy else current_proxy}", Fore.YELLOW)
            
            user = bot.get_user_info()
            if not user:
                raise Exception("Failed to get user info")
            
            bot.display_user_stats()
            
            while True:
                try:
                    user = bot.get_user_info()
                    if user:
                        last_claim = user.get('lastFaucetClaim')
                        
                        if last_claim is None:
                            bot.log_with_time("No previous faucet claim found. Attempting to claim...", Fore.YELLOW)
                            retry_count = 0
                            while retry_count < 5:
                                if bot.claim_faucet():
                                    break
                                retry_count += 1
                                if retry_count < 5:
                                    bot.log_with_time(f"Retrying faucet claim in 1 minute... (Attempt {retry_count}/6)", Fore.YELLOW)
                                    time.sleep(60)
                        else:
                            last_claim_date = datetime.strptime(last_claim, "%Y-%m-%dT%H:%M:%S.%fZ")
                            last_claim_date = last_claim_date.replace(tzinfo=timezone.utc)
                            
                            next_claim = last_claim_date + timedelta(hours=24)
                            now = datetime.now(timezone.utc)

                            if now >= next_claim:
                                retry_count = 0
                                while retry_count < 5:
                                    if bot.claim_faucet():
                                        break
                                    retry_count += 1
                                    if retry_count < 5:
                                        bot.log_with_time(f"Retrying faucet claim in 1 minute... (Attempt {retry_count}/6)", Fore.YELLOW)
                                        time.sleep(60)

                        bot.display_user_stats()
                    bot.perform_random_task()
                    time.sleep(5)  # Add small delay between operations

                except Exception as e:
                    bot.log_with_time(f"Error occurred: {str(e)}", Fore.RED)
                    time.sleep(60)  # Wait a minute before retrying

        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"{Fore.RED}Error with proxy {current_proxy}: {str(e)}")
                print(f"{Fore.YELLOW}Retrying with different proxy... (Attempt {retry_count + 1}/{max_retries}){Style.RESET_ALL}")
                time.sleep(5)  # Wait before trying next proxy
            else:
                print(f"{Fore.RED}Failed to connect after {max_retries} attempts with different proxies. Stopping.{Style.RESET_ALL}")
                break

def main():
    banner = """
╔══════════════════════════════════════════════╗
║           Blockpad Task Automate             ║
║     Github: https://github.com/im-hanzou     ║
╚══════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)
    
    tokens = load_tokens()
    if not tokens:
        print(f"{Fore.RED}No tokens found in tokens.txt. Please add at least one token.{Style.RESET_ALL}")
        return

    proxies = load_proxies()
    if not proxies:
        print(f"{Fore.RED}No proxies found in proxy.txt. Please add at least one proxy.{Style.RESET_ALL}")
        return

    print(f"{Fore.GREEN}Loaded {len(tokens)} tokens and {len(proxies)} proxies{Style.RESET_ALL}")

    threads = []
    for i, token in enumerate(tokens):
        proxy = proxies[i % len(proxies)] if proxies else None
        thread = threading.Thread(target=run_account, args=(token, proxy, proxies))
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Small delay between starting threads

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping all bots...{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()
