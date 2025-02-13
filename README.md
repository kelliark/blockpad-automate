# Blockpad Automate
Blockpad Testnet automate perform task script.
- Another script, [Blockpad Autoref](https://github.com/im-hanzou/blockpad-autoref)

## Tools and components required
1. Blockpad Account, Register here: [https://testnet.blockpad.fun/register](https://testnet.blockpad.fun/register)
2. Blockpad Account Bearer Token(s)
3. VPS or RDP (OPTIONAL)
4. Proxies (OPTIONAL)

## Multi-Account Support
The script now supports running multiple accounts simultaneously. To use this feature:

1. Open a file named `tokens.txt` in the same directory as the script
2. Add one bearer token per line in the file
3. Each token will run in its own thread

Example `tokens.txt`:
```
eyJhbGciXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
eyJhbGciYYYYYY.YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
eyJhbGciZZZZZZ.ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
```

## AutoFetch Token from the Autoref
[Auto Token Fetch](https://github.com/kelliark/blockpad-automate/discussions/1)

## Proxy Support
The script supports both HTTP and SOCKS5 proxies with authentication. To use proxies:

1. Open a file named `proxy.txt` in the same directory as the script
2. Add your proxies one per line in any of these formats:
   - `username:password@host:port`
   - `host:port`
   - `http://username:password@host:port` (recommended)
   - `socks5://username:password@host:port`

The script will automatically:
- Create both HTTP and SOCKS5 versions of each proxy
- Handle authentication if provided
- Retry with different proxies if one fails
- Distribute proxies among accounts

Example `proxy.txt`:
```
user1:pass1@proxy1.example.com:8080
user2:pass2@proxy2.example.com:1080
proxy3.example.com:8080
```

## Installation
```bash
git clone https://github.com/kelliark/blockpad-automate
```

### Requirements installation
- Make sure you already in bot folder:
```bash
cd blockpad-automate
```

```bash
pip install -r requirements.txt
```

## Run the Bot
- Windows and Termux:
```bash
python main.py
```

- The script will automatically load tokens from `tokens.txt` and proxies from `proxy.txt` if they exist
- If these files don't exist, it will prompt for a single bearer token

## Features
- Multi-account support
- HTTP and SOCKS5 proxy support with authentication
- Automatic proxy rotation on failure
- Concurrent account processing
- Error handling and automatic retries
- Detailed logging with colored output

# Notes
- Run this bot, use my referral code if you don't have one.
- You can just run this bot at your own risk, I'm not responsible for any loss or damage caused by this bot.
- This bot is for educational purposes only.
- When using proxies, ensure they are reliable and have good uptime.
- The script includes retry mechanisms, but very unstable proxies may still cause issues.
- Thanks to the real owner of this respo, I just add something a little bit for myself but you can use it if you want
