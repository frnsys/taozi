import os
from whoosh import index
from whoosh.writing import AsyncWriter
from whoosh.fields import Schema, ID, TEXT
from whoosh.qparser import MultifieldParser

schema = Schema(id=ID(unique=True, stored=True),
                title=TEXT,
                body=TEXT,
                desc=TEXT,
                subtitle=TEXT,
                tags=TEXT,
                authors=TEXT)

# Create or load index
INDEX_DIR = 'post_ix'
if not index.exists_in(INDEX_DIR):
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)
    ix = index.create_in(INDEX_DIR, schema)
else:
    ix = index.open_dir(INDEX_DIR)

def index_post(post):
    """Add or update a post's search entry"""
    writer = AsyncWriter(ix)
    writer.update_document(
        id=str(post.id),
        title=post.title,
        body=post.body,
        desc=post.desc,
        subtitle=post.subtitle,
        tags=post.tags,
        authors=' '.join([a.name for a in post.authors]))
    writer.commit()

def unindex_post(post):
    """Delete a post from the search index"""
    writer = AsyncWriter(ix)
    writer.delete_by_term('id', str(post.id))
    writer.commit()

def search_posts(query):
    with ix.searcher() as searcher:
        query = MultifieldParser(['title', 'body', 'tags', 'desc', 'subtitle', 'authors'], ix.schema).parse(query)
        results = [int(r['id']) for r in searcher.search(query, limit=None)]
    return results
