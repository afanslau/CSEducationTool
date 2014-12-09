# from django.utils import timezone
from django.db import models
from django.db.utils import IntegrityError
from scripts.Helpers import ensurePrefix
# from sodata.AutoUpdateDateTimeField import AutoUpdateDateTimeField
import datetime



class Resources(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(default=datetime.datetime.now)


    #CONSTRAINT - When 

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
        #How can I make it return a query set instead of converting to a list

        #   Avoid returning [None] when the child TopicRelations 
        #     relation.to_resource should never be None!!
        return [relation.to_resource for relation in TopicRelations.objects.filter(from_resource=self).select_related('to_resource')] # HOW TO USE **kwargs to let the user provide a filter

    def get_parent_resources(self):
        return [relation.from_resource for relation in TopicRelations.objects.filter(to_resource=self).select_related('from_resource')]

    def get_top_level():
        return Resources.objects.filter(parent_topics=None)

    def to_dict(self):
        return {'id':self.id, 'title':self.title, 'text':self.text, 'url':self.url}

    #May need this save() override, not sure yet

    def save(self, *args, **kwargs):
        has_title = self.title is not None
        has_text = self.text is not None
        has_url = self.url is not None
        if not has_title and not has_text and not has_url:
            raise ValueError("At least one of the columns [title,text,url] must have a value")
        elif has_url and not has_title:
            self.title = "Set the title to the web page title"
            if not has_text:
                self.text = "if the text is empty, Set the text to the first paragraph of the web page"
        
        # Make sure that the url is absolute
        if has_url: self.url = ensurePrefix(self.url,'http://') 

        # Update the created and modified fields
        if not self.id:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()


        super(Resources, self).save(*args, **kwargs)  #returns self casted as its superclass Resources?? but the superclass is Model.. Look this up later

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
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {'id':self.id, 'from_resource':self.from_resource.to_dict(), 'to_resource':self.to_resource.to_dict()}

    def save(self, *args, **kwargs):
        # Update the created and modified fields
        if not self.id:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        super(TopicRelations, self).save(*args, **kwargs)





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

