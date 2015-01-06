from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from scripts.Helpers import ensurePrefix
# from sodata.AutoUpdateDateTimeField import AutoUpdateDateTimeField
import datetime, urllib, urllib2
from urlparse import urlparse
from operator import itemgetter
from bs4 import BeautifulSoup as Soup
import watson


# Cache update time
CACHE_UPDATE_TIME = datetime.timedelta(days=10)
TITLE_EXTRACT_LENGTH = 100
TEXT_PREVIEW_LENGTH = 200
TEXT_EXTRACT_LENGTH = 600



class Resources(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    html_text = models.TextField(blank=True, null=True)

    # Do multi-field blank/null constraints exist?

    display_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    full_page_cache = models.TextField(blank=True, null=True)
    last_cache_time = models.DateTimeField(blank=True, null=True)

    # Algorithmicly determined rating
    # is dependent on users and context, so I think this should be stored in a UserActivity model...
    author = models.ForeignKey(User, blank=True, null=True) # Should default to the system admin or anon user
    rating = models.IntegerField(blank=True, null=False, default=0)

    # DateTime fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    # last_visited = models.ForeignKey(UserActivity) stores the activity of a user interacting with this object

    # Internal Flags
    pre_seeded = models.BooleanField(default=False)
    in_standard = models.BooleanField(default=False)
    human_created = models.BooleanField(default=True)
    bing_id = models.CharField(blank=True, null=True, unique=True, max_length=100)

    # _property = models.TextField()  # Could use this to store the preview so we don't have to calculate it each time, but I think time is a better trade off than duplicating db storage
    @property
    def preview(self):
        _text = self.html_text if self.html_text is not None else self.text
        return Resources.preview_html(_text, max_length=TEXT_PREVIEW_LENGTH)

    @classmethod
    def preview_html(cls, html_text, max_length=None):
        
        maxlen = max_length if max_length is not None else TEXT_PREVIEW_LENGTH
        _text = html_text

        # Error checking
        if _text is None: return None 


        #Parse out the first full HTML tag under n characters long
        allp = Soup(_text).find_all('p')

        # if there are no p tags, return the truncated text
        if len(allp) == 0:
            return _text[0:maxlen]

        # else get the lenths of each p tag
        lens = [len(p.string) for p in allp]

        # Cut the page to only the first 500 characters
        isum = 0
        i = 0
        while isum<maxlen and i < len(lens):
            isum += lens[i]
            i+=1
            
        # Return the concatenated string
        prev = ' '.join([p.string if p.string is not None else '' for p in allp[0:i]])
        return prev

    def __unicode__(self):
        return self.title 

    '''

    ManyToManyField did not work - for some reason when I added a child using 

        child_resource = Resources()
        child_resource.save()

        parent_resource = Resources()
        parent_resource.save()

        parent_resource.child_resources.add(child_resource)
        parent_resource.save()

        The relationships were being set in the wrong direction

    '''

    # child_resources = models.ManyToManyField('self', related_name='parent_topics')  #Cannot be blank, What is the advantage of using URLField over TextField or CharField
    # topic_child = models.ForeignKey(Topics, blank=True, null=True, related_name='parent_topics')
    # topic_parent = models.ForeignKey(Topics, blank=True, null=True, related_name='resource_list')
    
    def get_child_resources(self, **kwargs):
        #Select related makes this run in one query. 
        #How can I make it return a QuerySet instead of converting to a list

        # Check kwargs - By default only get the human created children
        if 'human_created' not in kwargs:
            kwargs['human_created'] = True

        #   Avoid returning [None] when the child TopicRelations 
        #     relation.to_resource should never be None!!
        out = Resources.objects.filter(parent_resources__from_resource=self, **kwargs)
        # out = [relation.to_resource for relation in TopicRelations.objects.filter(from_resource=self).select_related('to_resource').filter(**kwargs)] # HOW TO USE **kwargs to let the user provide a filter
        return None if len(out)==0 else out

    def get_parent_resources(self, **kwargs):
        if 'human_created' not in kwargs:
            kwargs['human_created'] = True
        out = Resources.objects.filter(child_resources__to_resource=self, **kwargs)
        # out = [relation.from_resource for relation in TopicRelations.objects.filter(to_resource=self).select_related('from_resource').filter(**kwargs)]
        return None if len(out)==0 else out

    # Creates and/or adds a resource to self as a child
    def add_child_resource(self, inchild=None, **kwargs):
        child = inchild
        if child is None:
            child = Resources(**kwargs)
        if child.id is None:
            child.save()

        tr = TopicRelations(from_resource=self, to_resource=child)
        tr.save()
        return child

    def get_top_level():
        return Resources.objects.filter(parent_topics=None)

    def to_dict(self):
        return {'id':self.id, 'title':self.title, 'text':self.text, 'url':self.url}



    # Cache site
    def update_page_cache(self):
        if self.url is None:
            return

        if self.full_page_cache is None or timezone.now() - self.last_cache_time > CACHE_UPDATE_TIME:
            # Try to download and cache the page
            try: 
                self.full_page_cache = urllib2.urlopen(self.url).read()
                self.last_cache_time = timezone.now()
            except urllib2.HTTPError, e:
                print('update_page_cache HTTPError = ' + str(e.code))
            except urllib2.URLError, e:
                print('update_page_cache URLError = ' + str(e.reason))
            except httplib.HTTPException, e:
                print('update_page_cache HTTPException')
            except Exception:
                import traceback
                print('update_page_cache generic exception: ' + traceback.format_exc())

        

    def save(self, *args, **kwargs):
        # Set up
        has_title = self.title is not None
        has_text = self.text is not None
        has_url = self.url is not None

        # Default title and text values
        if not has_title and not has_text and not has_url:
            raise ValueError("At least one of the columns [title,text,url] must have a value")
        
        # Make sure that the url is absolute and set display_url if it is none
        if has_url: 
            parse_result = urlparse(self.url)
            if parse_result.netloc == '': #No http was provided
                self.url = 'http://'+parse_result.geturl()
                parse_result = urlparse(self.url)
            # Set display_url if it is none
            if self.display_url is None:
                self.display_url = parse_result.netloc + parse_result.path

        # Cache the site if stale or None
        self.update_page_cache()
        
        # If text or title are not provided, extract them from the html page
        if has_url:
            site_title = u'' if self.full_page_cache is None else Soup(self.full_page_cache).title.text # Convert from unicode.. should probably handle this better
            text_prefix = u''
            if not has_title:
                self.title = site_title
            else: # If the user sets a title, set the site title as the first line in the text
                text_prefix = site_title
            print type(text_prefix), text_prefix
            if not has_text:
                self.text = text_prefix + u'\n' + Resources.preview_html(html_text=self.full_page_cache, max_length=TEXT_EXTRACT_LENGTH).encode('unicode')
                print self.text
                

        # If the title is still not set, take from the text or the url
        if self.title is None:
            if self.text is not None:
                self.title = self.text[:TITLE_EXTRACT_LENGTH]
            else: # self.url is not None
                pr = urlparse(self.url)
                self.title = self.display_url

        # Update the created and modified fields
        if self.id is None:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()

        print 'Will Save ' ,self.id, self.title

        super(Resources, self).save(*args, **kwargs)  #returns self casted as its superclass Resources?? but the superclass is Model.. Look this up later

# Uncomment when I can index my database...
# watson.register(Resources)

class TopicRelations(models.Model):
    id = models.AutoField(primary_key=True)

    # How can I make a cascade delete rule?
    '''
    Cascade delete the parent TopicRelations  when a Resources gets deleted  -  

    Should have no dangling TopicRelations objects

        Any TopicRelations objects without a to_resource should be deleted

        Any TopicRelations without a from_resource should display on some dangling resource page

    '''


    from_resource = models.ForeignKey(Resources, related_name='child_resources')
    to_resource = models.ForeignKey(Resources, related_name='parent_resources')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {'id':self.id, 'from_resource':self.from_resource.to_dict(), 'to_resource':self.to_resource.to_dict()}

    def save(self, *args, **kwargs):
        # Update the created and modified fields
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(TopicRelations, self).save(*args, **kwargs)




class UserActivity(models.Model):
    # Votes/Rating/Feedback
    STARRED = 0
    CREATED_RELATION = 1
    REMOVED_RELATION = 2
    # User interactions
    CREATED = 3
    EDITED = 4
    VISITED = 5
    

    Activity_Types = (
        (STARRED, 'Starred'),
        (CREATED, 'Created'),
        (EDITED, 'Edited'),
        (VISITED, 'Visited'),
        (REMOVED_RELATION, 'Not a relevant resource to its parent'),
        (CREATED_RELATION, 'Add ')
    )

    user = models.ForeignKey(User) # required
    resource = models.ForeignKey(Resources)
    activity_type = models.IntegerField(choices=Activity_Types, default=CREATED)

class UserRelation(models.Model): # Integrate this with django user groups and permissions
    VIEWER = 0
    AUTHOR = 1
    UserTypes = ((VIEWER,"Viewer"), (AUTHOR,"Author"))

    user = models.ForeignKey(User)
    resource = models.ForeignKey(Resources)

    user_type = models.IntegerField(choices=UserTypes, default=VIEWER)
    starred = models.BooleanField(default=False)
    num_visits = models.IntegerField(default=0) # How can I make this increment every time the model is accessed by the user?
    last_visited = models.DateTimeField(default=resource.updated_at)


class TopicGraph(object):
    """Abstract Class that provides methods on the Resources in the graph... Should this be initializable? """

    # Cite: http://stackoverflow.com/questions/24728612/best-way-in-python-to-make-a-class-that-is-uninitializable-but-whose-child-class
    def __new__(cls):
        if cls is Base:
          raise NotImplementedError()
        super(TopicGraph, cls).__new__(cls)

    ''' This really only makes sense if the graph is acyclic '''
    def get_root_resources():
        return Resources.objects.filter(parent_resource=None)
    # EndCitation

