---
layout: page
title: books read by year
permalink: /books/
---
<div class="year-list">
    <ul>
    {% for year in site.books reversed %}
        <li><a href="{{ year.url }}">{{ year.short-title }}</a></li>
    {% endfor %}
    </ul>
</div>