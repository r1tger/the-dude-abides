{{ contents }}
{% if notes_to|length > 0 %}
## Referenties

{% for b, note, paths in notes_to %}
* {{ note|format_note(b, exit_notes) }}
{% for path in paths %}
{% if path|length > 2 %}
[[{{ loop.index }}](?note={{ path|join('&amp;note=') }})]{% if not loop.last %}, {% endif %}

{% endif %}
{% endfor %}
{% endfor %}

{% endif %}
