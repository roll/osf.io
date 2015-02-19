<script type="text/html" id="gdrive_file_added">
added file
<a class="overflow">{{params.path }}</a> to
Google Drive in {{ nodeType }}
<a class="log-node-title-link overflow" data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>


<script type="text/html" id="gdrive_file_updated">
updated file
<a class="overflow">{{params.path}}</a> to
Google Drive in {{ nodeType }}
<a class="log-node-title-link overflow" data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>


<script type="text/html" id="gdrive_file_removed">
removed file <span class="overflow">{{ params.path }}</span> from
Google Drive in {{ nodeType }}
<a class="log-node-title-link overflow" data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>


<script type="text/html" id="gdrive_folder_selected">
linked Google Drive folder <span class="overflow">{{ params.folder }}</span> to {{ nodeType }}
<a class="log-node-title-link overflow" data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>


<script type="text/html" id="gdrive_node_deauthorized">
deauthorized the Google Drive addon for {{ nodeType }}
<a class="log-node-title-link overflow"
    data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>


<script type="text/html" id="gdrive_node_authorized">
authorized the Google Drive addon for {{ nodeType }}
<a class="log-node-title-link overflow"
    data-bind="attr: {href: nodeUrl}">{{ nodeTitle }}</a>
</script>
