# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
import ListField

# class AuthGroup(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     name = models.CharField(unique=True, max_length=80)

#     class Meta:
#         managed = False
#         db_table = 'auth_group'


# class AuthGroupPermissions(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     group = models.ForeignKey(AuthGroup)
#     permission = models.ForeignKey('AuthPermission')

#     class Meta:
#         managed = False
#         db_table = 'auth_group_permissions'


# class AuthPermission(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     name = models.CharField(max_length=50)
#     content_type = models.ForeignKey('DjangoContentType')
#     codename = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'auth_permission'


# class AuthUser(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     password = models.CharField(max_length=128)
#     last_login = models.DateTimeField()
#     is_superuser = models.BooleanField(default=False)
#     username = models.CharField(unique=True, max_length=30)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     email = models.CharField(max_length=75)
#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
#     date_joined = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'auth_user'


# class AuthUserGroups(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     user = models.ForeignKey(AuthUser)
#     group = models.ForeignKey(AuthGroup)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_groups'


# class AuthUserUserPermissions(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     user = models.ForeignKey(AuthUser)
#     permission = models.ForeignKey(AuthPermission)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_user_permissions'


# class Comments(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     post_id = models.IntegerField(blank=True, null=True)
#     score = models.IntegerField(blank=True, null=True)
#     text = models.TextField(blank=True)
#     creation_date = models.DateField(blank=True, null=True)
#     user_id = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'comments'


# class DjangoAdminLog(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     action_time = models.DateTimeField()
#     object_id = models.TextField(blank=True)
#     object_repr = models.CharField(max_length=200)
#     action_flag = models.SmallIntegerField()
#     change_message = models.TextField()
#     content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
#     user = models.ForeignKey(AuthUser)

#     class Meta:
#         managed = False
#         db_table = 'django_admin_log'


# class DjangoContentType(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     name = models.CharField(max_length=100)
#     app_label = models.CharField(max_length=100)
#     model = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'django_content_type'


# class DjangoMigrations(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     app = models.CharField(max_length=255)
#     name = models.CharField(max_length=255)
#     applied = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_migrations'


# class DjangoSession(models.Model):
#     session_key = models.CharField(primary_key=True, max_length=40)
#     session_data = models.TextField()
#     expire_date = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_session'


# class Posts(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     post_type_id = models.SmallIntegerField(blank=True, null=True)
#     parent = models.ForeignKey('self', blank=True, null=True, db_column='parent_id', related_name='question')
#     accepted_answer = models.ForeignKey('self', blank=True, null=True, db_column='accepted_answer_id', related_name='question_accepted')
#     creation_date = models.DateField(blank=True, null=True)
#     score = models.SmallIntegerField(blank=True, null=True)
#     view_count = models.IntegerField(blank=True, null=True)
#     body = models.TextField(blank=True)
#     owner_user_id = models.IntegerField(blank=True, null=True)
#     last_editor_user_id = models.IntegerField(blank=True, null=True)
#     last_editor_display_name = models.TextField(blank=True)
#     last_edit_date = models.DateField(blank=True, null=True)
#     last_activity_date = models.DateField(blank=True, null=True)
#     community_owned_date = models.DateField(blank=True, null=True)
#     closed_date = models.DateField(blank=True, null=True)
#     title = models.TextField(blank=True)
#     tags = ListField.ListField(blank=True)
#     answer_count = models.SmallIntegerField(blank=True, null=True)
#     comment_count = models.SmallIntegerField(blank=True, null=True)
#     favorite_count = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'posts'


# class UniqueTags(models.Model):
#     tag_text = models.TextField(blank=True)
#     id = models.AutoField(primary_key=True)

#     class Meta:
#         managed = False
#         db_table = 'unique_tags'

# class TaggedPosts(models.Model):
#     id = models.AutoField(primary_key=True)
#     post = models.ForeignKey(Posts, blank=True, null=True, db_column='post_id')
#     tag = models.ForeignKey(UniqueTags, blank=True, null=True, db_column='tag_id')

#     class Meta:
#         managed = False
#         db_table = 'tagged_posts'



# class Users(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     reputation = models.IntegerField(blank=True, null=True)
#     creation_date = models.DateField(blank=True, null=True)
#     display_name = models.TextField(blank=True)
#     email_hash = models.TextField(blank=True)
#     last_access_date = models.DateField(blank=True, null=True)
#     website_url = models.TextField(blank=True)
#     location = models.TextField(blank=True)
#     age = models.SmallIntegerField(blank=True, null=True)
#     about_me = models.TextField(blank=True)
#     views = models.IntegerField(blank=True, null=True)
#     up_votes = models.IntegerField(blank=True, null=True)
#     down_votes = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'users'


# class Votes(models.Model):
#     id = models.IntegerField(primary_key=True)  # AutoField?
#     post_id = models.IntegerField()
#     vote_type_id = models.SmallIntegerField(blank=True, null=True)
#     creation_date = models.DateField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'votes'


class Topics(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    # children = models.ManyToManyField('self', blank=True, null=True, related_name='+')

class TopicRelations(models.Model):
    id = models.AutoField(primary_key=True)
    from_node = models.ForeignKey(Topics, related_name='to_relation')
    to_node = models.ForeignKey(Topics, related_name='from_relation')

class Resources(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)  #Cannot be blank, What is the advantage of using URLField over TextField or CharField
    topic_child = models.ForeignKey(Topics, blank=True, null=True, related_name='linked_resource')
    topic_parent = models.ForeignKey(Topics, blank=True, null=True, related_name='resource_list')



