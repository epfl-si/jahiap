## Integration

Code to add before **&lt;/body&gt;** :

~~~
<script type="text/javascript">
(function() { var s = document.createElement("script"); s.type = "text/javascript"; s.async = true; s.src = '//api.usersnap.com/load/a0a37883-1812-41bf-9389-b4116433a67c.js';
var x = document.getElementsByTagName('script')[0]; x.parentNode.insertBefore(s, x); })();
</script>
~~~

### Integration example :

http://test-web-wordpress.epfl.ch:9090

## Issues

Usersnap's rendering engine needs access to the site's static resources (images + stylesheets)
to be able to render the screens accurately.

### Workaround 1 :

Use the browser extensions.

Chrome :

https://chrome.google.com/webstore/detail/usersnap-visual-feedback/khehmhbaabkepkojebhcpjifcmojdmgd

Firefox :

https://addons.mozilla.org/en-US/firefox/addon/usersnap/

### Workaround 2 :

Configure the server to let usernap access :

https://usersnap.com/help/troubleshooting/protected

For nginx :

~~~
allow 144.76.224.70;
allow 78.46.60.85;
allow 136.243.88.28;
~~~