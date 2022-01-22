Datatable v2.0.0
================

[![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square)](LICENSE)

Datatable is a javascript plugin for dynamic datatables with pagination, filtering and ajax loading. This plugin **does not require jQuery** any longer since version 2.0.0.

How to use?
===========

Datatable is quite simple to use. Just add the CSS and Javascript files to your page:

```html
<script type="text/javascript" src="js/datatable.min.js"></script>
```

And run:

```javascript
var datatable = new DataTable(document.getElementById('MyTable'), {
    pageSize: 15,
    sort: '*'
});

datatable.loadPage(3);
var data = datatable.all();
datatable.deleteAll(function (e) {
    return e.title.trim().length > 0;
});
```

If you use jQuery:

```html
<script type="text/javascript" src="js/jquery.min.js"></script> 
<script type="text/javascript" src="js/datatable.min.js"></script>
<script type="text/javascript" src="js/datatable.jquery.min.js"></script>
```

And run:

```javascript
$('#MyTable').datatable({
    pageSize: 15,
    sort: '*'
}) ;

$('#MyTable').datatable('page', 3);
var data = $('#MyTable').datatable('select');
$('#MyTable').datatable('delete', function (e) {
    return e.title.trim().length > 0;
});

```

**Note:** If you are using bootstrap, use `datatable-boostrap.css` instead of `datatable.css`.

The full plugin documentation is available here: http://holt59.github.io/datatable

**Warning:** If you use bootstrap 2, you need to manually set the <code>pagingListClass</code> and <code>pagingDivClass</code> options to match bootstrap 2 pagination classes.

Copyright and license
=====================

The MIT License (MIT)

Copyright (c) 2016, Mikaël Capelle.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

See [LICENSE](LICENSE).
