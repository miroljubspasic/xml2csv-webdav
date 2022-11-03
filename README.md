1. copy/edit .env.example -> .env 

2. install xml2csv command

* 1st method - python (tested with v3.10)
  * ``pip install --editable .``
  * use command ``xml2csv`` to convert xml into csv and upload on Webdav srv

-----

* 2nd method - Docker

  * build container with ``docker build --tag py-xml2csv  . ``
  * use ``docker run -it py-xml2csv xml2csv`` to convert xml into csv and upload on Webdav srv


---

