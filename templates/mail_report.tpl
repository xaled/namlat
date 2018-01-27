<h1>{{ subject }}</h1><br>
{% for report in reports %}
<h2>{{ report.report_title }}</h2><br>
<b>{{ report.report_subtitle }}: </b>{{ url + report.report_uri }}<br>
<ul>
    {% for entry in report.entries %}
    <li>
        <b>{{ entry.title }}: </b>{{ entry.message_body}}.<br>
    </li>
    {% endfor %}
</ul>
{% endfor %}