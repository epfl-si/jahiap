### Integration

Code to add before **&lt;/body&gt;** :

~~~
<script type="text/javascript">
(function() { var s = document.createElement("script"); s.type = "text/javascript"; s.async = true; s.src = '//api.usersnap.com/load/a0a37883-1812-41bf-9389-b4116433a67c.js';
var x = document.getElementsByTagName('script')[0]; x.parentNode.insertBefore(s, x); })();
</script>
~~~

### Protected and Basic Authentication Sites

https://usersnap.com/help/troubleshooting/protected

For nginx :

~~~
allow 144.76.224.70;
allow 78.46.60.85;
allow 136.243.88.28;
~~~

http://test-web-wordpress.epfl.ch

