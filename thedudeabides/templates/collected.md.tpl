{% for note in notes %}
## {{ note.get_id() }}. {{ note.get_title() }}

{{ note.get_body() | replace('# ', '## ') }}

{% endfor %}
