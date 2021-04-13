{% for note in notes %}
# {{ note.get_title() }}

{{ note.get_body() }}

{% endfor %}
