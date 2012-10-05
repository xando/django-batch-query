from django.test import TransactionTestCase
from batch_query.tests.models import Entry, Section, Location


def _create_entries(count, **kwargs):
    return [
        Entry.objects.create(**dict(name=i, **kwargs)) for i in xrange(count)
    ]


class TestBatchSelect(TransactionTestCase):

    def test_select_related(self):
        section = Section.objects.create(name='s1')
        _create_entries(4, section=section)

        test_call = lambda: [
            e.section for e in Entry.objects.batch("section").all()
        ]

        self.assertNumQueries(2, test_call)
        self.assertEqual(4, len(test_call()))

    def test_select_related_with_null(self):
        section = Section.objects.create(name='s1')
        _create_entries(4, section=section)
        _create_entries(4)

        test_call = lambda: [
            e.section for e in Entry.objects.batch("section")
        ]

        self.assertNumQueries(2, test_call)
        self.assertEqual(8, len(test_call()))

    def test_select_related_many(self):
        section = Section.objects.create(name='s1')
        location = Location.objects.create(name='l1')
        _create_entries(10, section=section)
        _create_entries(10, location=location)

        test_call = lambda: [
            e.section for e in Entry.objects.batch("section", "location")
        ]

        self.assertNumQueries(3, test_call)
        self.assertEqual(20, len(test_call()))

    def test_select_related_many_chaine(self):
        section = Section.objects.create(name='s1')
        location = Location.objects.create(name='l1')
        _create_entries(10, section=section, location=location)

        test_call = lambda: [
            e.section for e in Entry.objects.batch("section")
                                            .batch("location")
        ]

        self.assertNumQueries(3, test_call)
        self.assertEqual(10, len(test_call()))

    def test_select_related_chaine_filter(self):
        section_1 = Section.objects.create(name='s1')
        location_1 = Location.objects.create(name='l1')
        section_2 = Section.objects.create(name='s2')
        location_2 = Location.objects.create(name='l2')

        _create_entries(10, section=section_1, location=location_1)
        _create_entries(10, section=section_2, location=location_2)

        test_call = lambda: [
            e.section for e in Entry.objects.batch("section")
                                            .batch("location")
                                            .filter(section=section_1)
        ]

        self.assertNumQueries(3, test_call)
        self.assertEqual(10, len(test_call()))

        test_call = lambda: [
            e.section for e in Entry.objects.filter(section=section_1)
                                            .batch("section")
                                            .batch("location")
        ]

        self.assertNumQueries(3, test_call)
        self.assertEqual(10, len(test_call()))
