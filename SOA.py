# parallel arrays

first_names = ['Joe',  'Bob',  'Frank',  'Hans'    ]
last_names = ['Smith','Seger','Sinatra','Schultze']
heights_in_cm = [169,     158,    201,      199      ]

for i in xrange(len(first_names)):
    print "Name: %s %s" % (first_names[i], last_names[i])
    print "Height in CM: %s" % heights_in_cm[i]

Using zip:
for first_name, last_name, height in zip(first_names, last_names, heights_in_cm):
    print "Name: %s %s" % (first_name, last_name)
    print "Height in CM: %s" % height_in_cm
    
