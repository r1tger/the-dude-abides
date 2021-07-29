{{ contents }}
{% if notes_to|length > 0 %}
## Referenties

{% for b, note in notes_to %}
{{ loop.index }}. {{ note|format_note(b, exit_notes) }}
{% endfor %}

{% endif %}

{% if lattices|length > 0 %}
## Lattices

{% for b, note, paths in lattices %}
{{ loop.index }}. {{ note|format_note(b, exit_notes) }}
{% for path in paths %}
[[{{ loop.index }}](?note={{ path|join('&amp;note=') }})]{% if not loop.last %}, {% endif %}

{% endfor %}
{% endfor %}

{% endif %}
