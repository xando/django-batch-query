from django.db.models.query import QuerySet
from django.db import models
from django.conf import settings

from replay import Replay


class Batch(Replay):
    # functions on QuerySet that we can invoke via this batch object
    __replayable__ = ('filter', 'exclude', 'annotate',
                      'order_by', 'reverse', 'select_related',
                      'extra', 'defer', 'only', 'batch')

    def __init__(self, fieldname, **filter):
        super(Batch,self).__init__()

        self.fieldname = fieldname

        if filter: # add a filter replay method
            self._add_replay('filter', *(), **filter)

    def clone(self):
        cloned = super(Batch, self).clone(self.fieldname)
        return cloned

class BatchQuerySet(QuerySet):

    def _clone(self, *args, **kwargs):
        query = super(BatchQuerySet, self)._clone(*args, **kwargs)
        batches = getattr(self, '_batches', None)
        if batches:
            query._batches = set(batches)
        return query

    def _create_batch(self, batch_or_str):
        batch = batch_or_str
        if isinstance(batch_or_str, basestring):
            batch = Batch(batch_or_str)

        return batch

    def _batch(self, model, instances, fieldname, filter=None):
        instances = list(instances)

        field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)

        if not m2m and direct:
            related_model = field_object.rel.to
            attr_name = "%s_%s" % (fieldname, related_model._meta.pk.name)

            related_objects = related_model._default_manager.in_bulk(
                [getattr(obj, attr_name, None) for obj in instances]
            )
            for instance in instances:
                setattr(instance, fieldname, related_objects.get(getattr(instance, attr_name)))

        return instances

    def batch(self, *batches, **named_batches):
        batches = getattr(self, '_batches', set()) | \
                  set(self._create_batch(batch) for batch in batches)

        query = self._clone()
        query._batches = batches
        return query

    def iterator(self):
        result_iter = super(BatchQuerySet, self).iterator()
        batches = getattr(self, '_batches', None)
        if batches:
            results = list(result_iter)
            for batch in batches:
                results = self._batch(self.model, results,
                                 batch.fieldname,
                                 batch.replay)
            return iter(results)
        return result_iter


class BatchManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return BatchQuerySet(self.model)

    def batch(self, *batches, **named_batches):
        return self.all().batch(*batches, **named_batches)
