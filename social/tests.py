from django.test import TestCase

# Create your tests here.
from social.models import Project



p1 = Project(
    title='My First Project',
    description='A web development project.',
    technology='Django',
    image='img/project1.png')
p1.save()