# 使用方法
` python manage.py db init`

` python manage.py db migrate`

` python manage.py db upgrade`

` python manage.py runserver -d -r`

##手动添加用户
`

>>> User.query.all()

[]

>>> u = User(username='a',email='a@a.com',password='abcdef')

>>> db.session.add(u)

>>> db.session.commit()

>>> User.query.all()

[<User u'a'>]

>>> exit()


`
