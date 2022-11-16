def findall(node, *args, **kwargs):
    """Compatibility for docutils <0.18."""
    return getattr(node, "findall", node.traverse)(*args, **kwargs)
