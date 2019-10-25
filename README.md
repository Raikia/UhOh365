# UhOh365
A script that can see if an email address is valid in Office365.  This does not perform any login attempts, is unthrottled, and is incredibly useful for social engineering assessments to find which emails exist and which don't.

Microsoft does not consider "email enumeration" a vulnerability, so this is taking advantage of a "feature".  There are a couple other public Office365 email validation scripts out there, but they all (that I have seen) require at least 1 login attempt per user account. That is **detectable** and can be found as a light bruteforce attempt (1 "common" password across multiple accounts).

This script allows for email validation with **zero login attempts** and only uses Microsoft's built-in Autodiscover API so it is invisible to the person/company who owns the email address.  Furthermore, this API call appears to be completely unthrottled and I was able to validate over 2,000 email addresses within 1 minute in my testing.

## Usage
The script is actually really basic and easy to use.  You make a file of the emails you want to see are valid or not and pass it as an argument to the script:

    Usage: UhOh365.py [-h] [-v] [-t THREADS] [-o OUTPUT] file
    
    positional arguments:
      file                  Input file containing one email per line

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Display each result as valid/invalid. By default only displays valid
      -t THREADS, --threads THREADS
                            Number of threads to run with. Default is 20
      -o OUTPUT, --output OUTPUT
                            Output file for valid emails only
      -n, --nossl           Turn off SSL verification. This can increase speed if
                            needed
      -p PROXY, --proxy PROXY
                            Specify a proxy to run this through (eg: 'http://127.0.0.1:8080')
                            
## Explanation
This is actually a very easy thing to do.  It turns out the `/autodiscover/autodiscover.json/v1.0/{EMAIL}?Protocol=Autodiscoverv1` API endpoint returns different status codes for if an email exists in o365 or not.  200 status code means it exists, a 302 means it doesn't exist.

If the email does exist:
![img](https://i.imgur.com/Ak88WKi.png)

If the email does **not** exist:
![img](https://i.imgur.com/bAnWuQZ.png)

Notice this request takes zero authentication or identifying parameters and it does not cause a login attempt on the target account.


## Author
Chris King

raikiasec@gmail.com

@raikiasec
