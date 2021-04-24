---
title: "Index"
date: "{{ date }}"
---

* |xx| [Register](register.html)
{% for b, note in top_notes %}
* {{ note|format_note(b, exit_notes) }}
{% endfor %}

# Ingang

{% for b, note in entry_notes %}
{{ loop.index }}. {{ note|format_note(b)}}
{% endfor %}

# Inbox

{% for b, note in inbox %}
{{ loop.index }}. {{ note|format_note(b)}}
{% endfor %}
