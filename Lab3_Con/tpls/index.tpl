<!DOCTYPE HTML>
<html>
<head>
<meta charset="utf-8">
<title>Стена</title>
</head>
<body>
   Please, enter your Login and password. If you do not have a login, we will create an account for you
    <form method="post" action="/cgi-bin/wall.py">
        Login: <input type="text" name="login">
        Password: <input type="password" name="password">
        <input type="hidden" name="action" value="login">
        <input type="submit" value="Init">
    </form>

    {posts}

    {publish}
	<br>
	{getdata}
</body>
</html>