=========================
QuerySet API Batch method
=========================

Query method batch is handy for minimizing the number of queries that need
to be made in certain situations.  However it is only usual for
pre-selecting ForeignKey_ relations.

Example Usage
=============

    from batch_query import BatchManager

    class Section(models.Model):
        name = models.CharField(max_length=32)

    class Location(models.Model):
        name = models.CharField(max_length=32)

    class Entry(models.Model):
        name = models.CharField(max_length=255)
        section  = models.ForeignKey(Section, blank=True, null=True)
        location = models.ForeignKey(Location, blank=True, null=True)

        objects = BatchManager()


    >>> Entry.objects.batch("section")
    >>> Entry.objects.batch("section", "location")
    >>> Entry.objects.batch("section").batch("location")
    >>> Entry.objects.batch("section").batch("location").filter(section=section_1)
