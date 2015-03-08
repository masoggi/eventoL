from cities.models import Country, Region, City, District, Place
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop as _noop
from image_cropping import ImageRatioField
from image_cropping.fields import ImageCropField

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^django\.contrib\.gis\.db\.models\.fields\.PointField"])


class Building(Place):
    address = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Building')
        verbose_name_plural = _('Buildings')


class Sede(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('Country'))
    state = models.ForeignKey(Region, verbose_name=_('State'))
    city = models.ForeignKey(City, verbose_name=_('City'))
    district = models.ForeignKey(District, verbose_name=_('District'), blank=True, null=True)
    place = models.ForeignKey(Building, verbose_name=_('Place'), help_text=_('Specific place (building) where the event is taking place'))
    name = models.CharField(_('Name'), max_length=200)
    date = models.DateField(_('Date'), help_text=_('Date of the event'))

    def __unicode__(self):
        return "%s / %s / %s - %s" % (self.country, self.state, self.city, self.name)


class Attendant(models.Model):
    name = models.CharField(_('First Name'), max_length=200, blank=True, null=True)
    surname = models.CharField(_('Last Name'), max_length=200, blank=True, null=True)
    nickname = models.CharField(_('Nickname'), max_length=200, blank=True, null=True)
    email = models.EmailField(_('Email'), max_length=200)
    sede = models.ForeignKey(Sede, verbose_name=_noop('Sede'), help_text=_('Sede you are going to attend'))
    assisted = models.BooleanField(_('Assisted'), default=False)
    is_going_to_install = models.BooleanField(_('Is going to install?'), default=False, help_text=_('Are you going to bring a PC for installing it?'))
    additional_info = models.TextField(_('Additional Info'), blank=True, null=True, help_text=_('i.e. Wath kind of PC are you bringing'))

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = _('Attendant')
        verbose_name_plural = _('Attendants')
        unique_together = ('email', 'sede',)


class Organizer(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'), blank=True, null=True)
    sede = models.ForeignKey(Sede, verbose_name=_noop('Sede'), help_text=_('Sede you are going to collaborate'))
    is_coordinator = models.BooleanField(_('Is Coordinator'), default=False, help_text=_('The user is the coordinator of the sede?'))
    phone = models.CharField(_('Phone'), max_length=200, blank=True, null=True)
    address = models.CharField(_('Address'), max_length=200, blank=True, null=True)
    assignation = models.CharField(_('Assignation'), max_length=200, blank=True, null=True, help_text=_('Assignations given to the user (i.e. Talks, Coffee...)'))
    additional_info = models.CharField(_('Additional Info'), max_length=200, blank=True, null=True, help_text=_('Any additional info you consider relevant'))
    assisted = models.BooleanField(_('Assisted'), default=False)
    time_availability = models.CharField(_('Time Availability'), max_length=200, blank=True, null=True, help_text=_('Time gap in which you can help during the event. i.e. "All the event", "Morning", "Afternoon"...'))

    def __unicode__(self):
        return str(self.user)

    class Meta:
        verbose_name = _('Organizer')
        verbose_name_plural = _('Organizers')


class HardwareManufacturer(models.Model):
    name = models.CharField(_('Name'), max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Hardware Manufacturer')
        verbose_name_plural = _('Hardware Manufacturers')


class Hardware(models.Model):
    type = models.CharField(_('Type'), choices=(('MOB', _('Mobile')),
                                     ('NOTE', _('Notebook')),
                                     ('NET', _('Netbook')),
                                     ('TAB', _('Tablet')),
                                     ('DES', _('Desktop')),
                                     ('OTH', _('Other')),),
                            max_length=200)
    manufacturer = models.ForeignKey(HardwareManufacturer, verbose_name=_('Manufacturer'), blank=True, null=True)
    model = models.CharField(_('Model'), max_length=200, blank=True, null=True)
    serial = models.CharField(_('Serial'), max_length=200, blank=True, null=True)

    def __unicode__(self):
        return "%s, %s, %s" % (self.type, self.manufacturer, self.model)


class Software(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    version = models.CharField(_('Version'), max_length=200)
    type = models.CharField(_('Type'), choices=(('OS', _('Operative System')),
                                     ('AP', _('Application')),
                                     ('SU', _('Support and Problem Fixing')),
                                     ('OT', _('Other')),),
                            max_length=200)

    def __unicode__(self):
        return "%s - %s v.%s" % (self.type, self.name, self.version)


class Installer(Organizer):
    level = models.CharField(_('Level'), choices=(('1', _('Beginner')),
                                      ('2', _('Medium')),
                                      ('3', _('Advanced')),
                                      ('4', _('Super Hacker')),),
                             max_length=200, help_text=_('Linux Knowledge level for an installation'))
    software = models.ManyToManyField(Software, verbose_name=_('Software'), blank=True, null=True, help_text=_('Select all the software you can install. Hold Ctrl key to select many'))

    class Meta:
        verbose_name = _('Installer')
        verbose_name_plural = _('Installers')


class Installation(models.Model):
    attendant = models.ForeignKey(Attendant, verbose_name=_('Attendant'), help_text=_('The owner of the installed hardware'))
    hardware = models.ForeignKey(Hardware, verbose_name=_('Hardware'), blank=True, null=True)
    software = models.ForeignKey(Software, verbose_name=_('Software'), blank=True, null=True)
    installer = models.ForeignKey(Installer, verbose_name=_('Installer'), related_name='installed_by', blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True, null=True, help_text=_('Any information or trouble you found and consider relevant to document'))

    def __unicode__(self):
        return "%s, %s, %s" % (self.attendant, self.hardware, self.software)

    class Meta:
        verbose_name = _('Installation')
        verbose_name_plural = _('Installations')


class TalkType(models.Model):
    '''
    Type of talk. For example: Talk, Workshop, Debate, etc.
    '''
    name = models.CharField(_('Name'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Talk Type')
        verbose_name_plural = _('Talk Types')


class TalkProposal(models.Model):
    title = models.CharField(_('Title'), max_length=600)
    speakers_email = models.CharField(_('Speakers Emails'), max_length=600, help_text=_("Comma separated speaker's emails"))
    labels = models.CharField(_('Labels'), max_length=200, help_text=_('Comma separated tags. i.e. Linux, Free Software, Debian'))
    abstract = models.TextField(_('Abstract'), help_text=_('Short idea of the talk (Two or three sentences)'))
    long_description = models.TextField(_('Long Description'))
    sede = models.ForeignKey(Sede, verbose_name=_noop('Sede'), help_text=_('Sede you are proposing the talk to'))
    presentation = models.FileField(_('Presentation'), upload_to='talks', blank=True, null=True, help_text=_('Any material you are going to use for the talk (optional, but recommended)'))
    type = models.ForeignKey(TalkType, verbose_name=_('Type'))
    home_image = ImageCropField(upload_to='talks_thumbnails', verbose_name=_('Home Page Image'), blank=True, null=True, help_text=_('Image that is going to appear in the home page of this web for promoting the talk (optional)'))
    cropping = ImageRatioField('home_image', '700x450', size_warning=True, verbose_name=_('Cropping'), help_text=_('The image must be 700x450 px. You can crop it here.'))
    dummy_talk = models.BooleanField(_('Dummy Talk?'), default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Talk Proposal')
        verbose_name_plural = _('Talk Proposals')


class Room(models.Model):
    sede = models.ForeignKey(Sede, verbose_name=_noop('Sede'))
    name = models.CharField(_('Name'), max_length=200, help_text=_('i.e. Classroom 256'))
    for_type = models.ForeignKey(TalkType, verbose_name=_('For talk type'), help_text=_('The type of talk the room is going to be used for.'))

    def __unicode__(self):
        return "%s - %s" % (self.sede.name, self.name)

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')


class TalkTime(models.Model):
    start_date = models.DateTimeField(_('Start Date'))
    end_date = models.DateTimeField(_('End Date'))
    sede = models.ForeignKey(Sede, verbose_name=_noop('Sede'))
    talk_type = models.ForeignKey(TalkType, verbose_name=_('Talk Type'), help_text=_('The type of talk the room is going to be used for.'))

    def __unicode__(self):
        return "%s - %s" % (self.start_date.strftime("%H:%M"), self.end_date.strftime("%H:%M"))

    class Meta:
        verbose_name = _('Talk Time')
        verbose_name_plural = _('Talk Times')


class Talk(TalkProposal):
    speakers = models.ManyToManyField(Organizer, related_name='speakers', verbose_name=_('Speakers'))
    room = models.ForeignKey(Room, verbose_name=_('Room'))
    hour = models.ForeignKey(TalkTime, verbose_name=_('Hour'))

    class Meta:
        verbose_name = _('Talk')
        verbose_name_plural = _('Talks')

class EventInfo(models.Model):
    sede = models.ForeignKey(Sede, verbose_name=_noop('Sede'))
    html = models.TextField()

    class Meta:
        verbose_name = _('Event Info')
        verbose_name_plural = _('Envent Info (s)')