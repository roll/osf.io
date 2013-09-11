<%inherit file="project.view.mako" />
<div class="row">
    <div class="span9">
        <form method="post">
            <div class="wmd-panel">
                <div id="wmd-button-bar"></div>
                <textarea class="wmd-input" id="wmd-input" name="content">${content}</textarea>
                <input type="submit" value="Save">
            </div>
            <div id="wmd-preview" class="wmd-panel wmd-preview"></div>
        </form>
    </div>
    <div class="span3">
        <div style="width:200px; float:right; margin-left:30px;">
        <%include file="_wiki_status.mako" />
        <%include file="_wiki_nav.mako" />
        </div>
    </div>
    <script type="text/javascript" src="/static/pagedown/Markdown.Converter.js"></script>
    <script type="text/javascript" src="/static/pagedown/Markdown.Sanitizer.js"></script>
    <script type="text/javascript" src="/static/pagedown/Markdown.Editor.js"></script>
    <script type="text/javascript">
        (function () {
            var converter1 = Markdown.getSanitizingConverter();
            var editor1 = new Markdown.Editor(converter1);
            editor1.run();
        })();
    </script>
</div>