## API key

a0a37883-1812-41bf-9389-b4116433a67c

## Integration

Code to add before **&lt;/body&gt;** :

~~~
<!-- Code for Usersnap -->
<script type="text/javascript">
  var _usersnapconfig = {
    emailRequired: true,
    hideTour: true
  };

  (function() { var s = document.createElement("script"); s.type = "text/javascript"; s.async = true; s.src = '//api.usersnap.com/load/a0a37883-1812-41bf-9389-b4116433a67c.js';

  var x = document.getElementsByTagName('script')[0]; x.parentNode.insertBefore(s, x); })();
</script>
~~~

### Integration example

http://test-web-wordpress.epfl.ch:9090

## Issue

Usersnap's rendering engine needs access to the site's static resources (images + stylesheets)
to be able to render the screens accurately.

### Workaround

Use the browser extensions.

Chrome :

https://chrome.google.com/webstore/detail/usersnap-visual-feedback/khehmhbaabkepkojebhcpjifcmojdmgd

Firefox :

https://addons.mozilla.org/en-US/firefox/addon/usersnap/
