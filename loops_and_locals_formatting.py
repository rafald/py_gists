#!/usr/bin/env python3 

emails = {
     'Bob': 'bob@example.com',
     'Alice': 'alice@example.com',
}

for i, (name, email) in enumerate(emails.items()) :
   #print(locals())
   #print(*locals())
   #print(**locals())
   print( name, email, i )
   print( '{name} →  {email}'.format(**locals()) ) #TODO why **? ANS:i indicate that argument is last ** in arg of format()
   print( "<%(name)s →  %(email)s>" % locals() )
   #print( f'{name} →  {email}' )

