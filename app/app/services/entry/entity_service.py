from ...models import Entry


class EntryService:
    @classmethod
    def get_entry_or_404(cls, slug):
        valid_statuses = (Entry.STATUS_DRAFT, Entry.STATUS_PUBLIC)
        return Entry.query.filter((Entry.slug == slug) & (Entry.status.in_(valid_statuses))).first_or_404()

    @classmethod
    def get_entries_ordered_by_date(cls):
        return Entry.query.order_by(Entry.created_timestamp.desc())
