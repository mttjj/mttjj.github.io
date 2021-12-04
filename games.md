---
layout: page
title: games
permalink: /games/
---
<div class="year-list">
    <ul>
    {% for year in site.games reversed %}
        <li><a href="{{ year.url }}">{{ year.short-title }}</a></li>
    {% endfor %}
    </ul>
</div>
