Al momento de referenciar imagenes , css , js de la carpeta Static 
-Utilizar esta estructura:

css
"<link rel="stylesheet" href="{{ url_for('static', filename='CSS/style.css') }}">"
js
"<script src="{{ url_for('static', filename='CSS/main.css') }}"></script>"
img
<img src="{{ url_for('static', filename='Img/search_button.png') }}">
