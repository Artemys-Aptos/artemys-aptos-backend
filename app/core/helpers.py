
def paginate(query, page: int, page_size: int):
    """Simple pagination utility."""
    return query.offset((page - 1) * page_size).limit(page_size).all()