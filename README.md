# JSParser

A python3 script using Tornado and JSBeautifier to parse relative URLs from JavaScript files. Useful for easily discovering AJAX requests when performing security research or bug bounty hunting.

**This Tool is created by @nahamsec and I have just done a few changes to make this tool work with MacOs and the latest dependencies.**

**Orginal Repo:** https://github.com/nahamsec/JSParser/

## Fix For pycurl error


```
pip3 uninstall pycurl 
pip3 install --no-cache-dir --global-option=build_ext --global-option="-L/usr/local/opt/openssl/lib" --global-option="-I/usr/local/opt/openssl/include"  pycurl
```

## Fix tested on
* MacOs Catalina
* Fedora

# Dependencies

- safeurl
- tornado
- jsbeautifier

# Installing

```
$ sudo python3 setup.py install
```

# Running

Run `handler.py` and then visit http://localhost:8008.

```
$ python3 handler.py
```

# Authors

- https://twitter.com/bbuerhaus/
- https://twitter.com/nahamsec/

# Inspired By

- https://twitter.com/jobertabma/

# References

 - http://buer.haus/2017/03/31/airbnb-web-to-app-phone-notification-idor-to-view-everyones-airbnb-messages/
 - http://buer.haus/2017/03/09/airbnb-chaining-third-party-open-redirect-into-server-side-request-forgery-ssrf-via-liveperson-chat/

# Changelog

1.0 - Release
