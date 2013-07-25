curl 'http://stage.ecofundsdatabase.org/ajax/investment/mapsource/?view=density&zoom=6' \
      -H 'Cookie: django_language=en; sessionid=445a6c9c356f16744a4185b06261f9b8; csrftoken=dvj7XAM3rCNX1rLWHiIaQHmZ5IEWRHbF' \
      -H 'Accept-Encoding: gzip,deflate,sdch' \
      -H 'Host: stage.ecofundsdatabase.org' \
      -H 'Accept-Language: en-US,en;q=0.8' \
      -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36' \
      -H 'Accept: application/json, text/javascript, */*; q=0.01' \
      -H 'Referer: http://stage.ecofundsdatabase.org/en/' \
      -H 'X-Requested-With: XMLHttpRequest' \
      -H 'Connection: keep-alive' --compressed > unformatted_original.json


curl 'http://localhost:8000/geo_api/investment/density?view=density&zoom=6' \
      -H 'Cookie: django_language=en; sessionid=445a6c9c356f16744a4185b06261f9b8; csrftoken=dvj7XAM3rCNX1rLWHiIaQHmZ5IEWRHbF' \
      -H 'Accept-Encoding: gzip,deflate,sdch' -H 'Host: stage.ecofundsdatabase.org' \
      -H 'Accept-Language: en-US,en;q=0.8' \
      -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36' \
      -H 'Accept: application/json, text/javascript, */*; q=0.01' \
      -H 'Referer: http://stage.ecofundsdatabase.org/en/' \
      -H 'X-Requested-With: XMLHttpRequest' \
      -H 'Connection: keep-alive' --compressed > unformatted_new.json

python -m json.tool unformatted_original.json > original.json
python -m json.tool unformatted_new.json > new.json
